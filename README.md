## Fine-tuning gpt-3.5-turbo-0613 for roleplay

This will be a somewhat straightforward write-up on how to fine-tune Turbo to be better at roleplay.
Some limitations and warnings first:
1) Right now you can only fine-tune `gpt-3.5-turbo` (`gpt-3.5-turbo-0613` specifically) which has 4K context. OAI said they have plans to allow fine-tuning GPT-4, but that'd probably cost a lot.
2) The cost of fine-tuning itself is quite low ($0.008 for 1K tokens of the dataset), but the main problem is the inference cost - because the fine-tuned model will be only used by you, the inference will cost 8 times more compared to normal 4K Turbo, which makes it almost half as expensive as GPT-4.
3) The fine-tune model cannot be shared between different OpenAI accounts, so the only way to have the "same" fine-tune is to run the fine-tune job on  all the separate accounts you want to use. I doubt it'll actually be 100% the same due to all the small inaccuracies (like how Turbo at temp=0 can behave differently), but should be close enough.
4) The dataset for the fine-tune has to be 100% SFW, because, to quote OpenAI - ["fine-tuning training data is passed through our Moderation API and a GPT-4 powered moderation system to detect unsafe training data that conflict with our safety standards"](https://openai.com/blog/gpt-3-5-turbo-fine-tuning-and-api-updates). The Moderation API is quite strict, so even things like "sucking on a finger" won't pass. Thankfully, my script already does safety checks so your dataset is unlikely to get flagged after upload.
5) The owner of the account will get an email when a fine-tune finishes. Of course this won't affect normal, legitimate users, but it's just a good thing to keep in mind ;)

The fine-tune I did was mostly an experiment, but from other anons' reviews it turned out to be somewhat successful - they reported that a fine-tune had higher-quality responses than the normal Turbo. Of course, to get good results from a fine-tune you need to have a high-quality dataset, for example using RP chats generated with GPT-4. This is really the same concept as fine-tuning smaller local models on GPT-4 output - Turbo can get "smarter" from seeing GPT-4 responses too.

Some prerequisites:
1) Python.
2) An OpenAI key. Even trial ones will work, but then you need a small dataset and/or a small number of epochs to not go over the $5 credit limit.


The dataset has to contain at least 10 chat example (user/assistant messages), meaning that in our case the dataset has to contain 10 example chats. I have a small test dataset that I've made myself.

Let's start. First of all, install Python, clone the repo, and install all requirements. This assumes a Linux environment, but should work on Windows too.
```
git clone https://github.com/CncAnon1/turbo_ft
cd turbo_ft
pip install -r requirements.txt
```

Then go to `modules/key.py` and change the OpenAI API key to your working one. 

Then you have to collect enough (at least 10) chat examples. I'd recommend you to generate them with a high-quality model like GPT-4, because if you use output from a bad model, Turbo is not going to get better at RP.

The repo has no automated scripts for converting SillyTavern chats into chats for the fine-tune, that is because 1) The dataset for the fine-tune has to contain messages as they would be when doing a request with the API 2) I'm lazy.

So, once you have a more-or-less complete chat in SillyTavern, here's how you make a json for it:
1) Create a json file in the `chats` folder (has to be unique, but can be any name).
2) In the browser, open DevTools (F12 in Chrome), go to the Network tab, and do a new message/swipe so that the frontend sends a request to the backend.
3) You should see a request named "generate_openai", click on it, then go to the "Payload" tab.
4) Here you should see the request payload, the only thing that's interesting to us is the "messages" key. Simply right-click on it and select "Copy value".
5) Paste the copied value into your JSON file.

Once you do this for all the chats you want to fine-tune on, the main process is complete, but I highly recommend cleaning up and polishing your chat files:
1) Make sure all of them have the same first system message (the main prompt for the AI).
2) Merge multiple system messages into the first one.
3) Remove any jailbreak (the ones that appear just before the user message) or empty system messages.
4) **Use different names for different chats**. This can be done in SillyTavern itself by changing personas, or just with Find + Replace in the chat file itself. If all of your chats have the same user name, it might make the AI associate roleplaying with your name specifically or something, not sure. Do not forget to change the names in the system prompt if you copy the same one in all chats (from the 1st point).

You can always refer to the `chats_example` folder if you want to try fine-tuning without collecting your own chat files, or just want to see an example of a bit of "polishing". I honestly don't know if I should include the RP prompt in the examples or not, this requires much more experimentation.

Once all this is done, you can star the actual fine-tune.
First, run a check on your dataset:
```
python main.py check
```

This will run some basic sanity checks, like properly-formatted entries, roles. It will also run all of your messages through the Moderation API to ensure that none of the messages will trip the safety checks in the fine-tune process.

Once that is done and everything's fine, you can run:
```
python main.py format
python main.py upload
```

The first command merges all chat entries into a single `data.jsonl` file, the second one actually uploads it to the OpenAI for the fine-tune process. The second command should write the file ID in a file named `file_id.txt`. After the upload, wait like 10-20 seconds, because the file on OpenAI doesn't become instantly ready.

If all that is fine, you can start the fine-tune process:
```
python main.py start
```

Once the process started, you can check on its progress with:
```
python main.py status
```

This will list the latest events related to your fine-tune, and, when it's done, show you the model ID. Afterwards you can use this model ID to use your fine-tune. 

An important thing to note: not all frontends support specifying custom model names to use with the API. Specifically, for SillyTavern you have to use the key directly, then enable `Show "External" models (provided by API)` below the "OpenAI Model" dropdown, and then select the fine-tune ID from the model drop-down.

That should be all, enjoy using your fine-tune!


Some notes:
1) There's a `n_epochs` option in the config - it controls how many times the fine-tune will "show" the model your dataset. I think 20 should be a good option for small datasets, but if you have a bigger dataset, you might want to lower this value.