# Congressional Record Analysis

## (Work in Progress)
*This repository is an active work in progress. Feel free to look through it for interest, but the analysis is ongoing.*

### Overview
This repository aims to use the congressional record to analyze the number of motions of a particular member of Congress.
In particular, it aims to do three things:

1. **Scrape all of the files** from the Congressional Record. 
2. **Parse the text** in each Congressional Record and use Regex/NLP to create metrics describing the overall "activity" of a Member of Congress. 
3. **Correlate these metrics** against other metrics associated with that Member of Congress (i.e. voting record, positions of power, etc.). 


### Congressional Record 
The [Congressional Record](https://www.congress.gov/congressional-record) is the official daily record of Congress's proceedings, actions, and debates.
It is a way for every action, speech, motion, etc. made by a Member of Congress to be recorded for posterity. 
The average record for a daily edition is about ~100 pages long. 
That's a lot of text! 
Here's some sample text from the *[February 23, 2021](https://www.congress.gov/117/crec/2021/02/23/CREC-2021-02-23-senate.pdf)* Senate edition of the Record:

    Mr. CASEY. Mr. President, I ask unanimous consent that the Senate proceed to legislative session and be in a period of morning business, with Senators permitted to speak therein for up to 10 minutes each. The PRESIDING OFFICER. Without objection, it is so ordered." 

As you can see, a section starts with the speaker (in this cae, both **Mr. Casey** at the beginning and the **Presiding Officer** later), then who they are speaking to (usually the head of the Chamber), and then their request/speech. In this case, Senator Casey is addressing the President of the Senate to motion for unanimous consent on what is otherwise trifling morning business.

