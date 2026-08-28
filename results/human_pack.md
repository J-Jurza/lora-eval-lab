# Human blind pass

Score each side 1 to 5 per dimension, then a preference, before running the judge.
Fill the SCORES line exactly: `SCORES: A f c fo co | B f c fo co | PREF: A|B|tie | REASON: ...`

# Judging rubric

Score each output 1 to 5 on each dimension, then state a preference (A, B, or tie) with one
sentence. Judge the note against the **dialogue**, not against the reference; the reference
is shown only to calibrate format and expected level of detail.

| Dimension | 5 | 1 |
|---|---|---|
| **Faithfulness** | Every fact in the note is stated or clearly implied in the dialogue | Contains a fact the dialogue does not support |
| **Completeness** | Every clinically relevant fact in the dialogue for this section is captured | Major omissions |
| **Format** | Reads as the requested section of a clinical note | Wrong section, chatty, or not a note |
| **Concision** | No padding, no repetition | Verbose or repetitive |

Faithfulness outranks everything: a shorter note with no invented facts beats a fuller note
with one. A tie is a legitimate verdict.


---


## Pair test1:4

**Section:** Family and Social History

**Conversation:**

```
Doctor: Can you tell me about your family? Did anyone in your family have any medical problems? 
Patient: Oh yeah. My father died of thoracic aortic aneurysm. He was seventy one years old at that time. 
Doctor: Anything for anyone else? 
Patient: Yeah, my mom died of stroke. She was around eighty one.
```

**Reference (calibration only):**

```
Father died of a thoracic aortic aneurysm, age 71. Mother died of stroke, age 81.
```

**A:**

```
Family and Social History:
- Father: Died of thoracic aortic aneurysm at age 71
- Mother: Died of stroke at age 81
```

**B:**

```
Father died of thoracic aortic aneurysm at the age of 71. Mother died of stroke at the age of 81.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:7

**Section:** Family and Social History

**Conversation:**

```
Doctor: What is your family medical history? 
Patient: My parents do not have any health conditions. I have two half brothers that are in good health as well. 
Doctor: How old are your brothers? 
Patient: Twenty six and twenty eight. My grandmother on my mom's side had D V T in her leg. I think she was in her forty's.
Doctor: Any family history of diabetes? 
Patient: I think my aunt from my dad's side of the family and my cousins on my mom's side of the family are diabetic? Oh. My great grandfather had bone cancer.  He was in his eighties. My mom's brother was recently diagnosed with leukemia. He is around fifty years old. Then my dad's dad had colon cancer at seventy three. He had it since he was sixty eight, though. I think that is it.
```

**Reference (calibration only):**

```
Two half-brothers, ages 26 and 28, both in good health.  Parents are in good health.  A maternal great-grandmother had a deep venous thrombosis (DVT) of leg in her 40s.  A maternal great-uncle developed leukemia around age 50.  A maternal great-grandfather had bone cancer around age 80.  His paternal grandfather died of colon cancer at age 73, which he had had since age 68.  Adult-onset diabetes is present in distant relatives on both sides.
```

**A:**

```
Family and Social History:
- No known health conditions in the patient's family.
- Two half brothers are in good health.
- Grandmother on the patient's mother's side had DVT in her leg.
- Aunt from the patient's father's side and cousins on the mother's side are diabetic.
- Great grandfather had bone cancer at age 80.
- Patient's mother's brother was recently diagnosed with leukemia at age 50.
- Patient's father's father had colon cancer at age 73.
```

**B:**

```
Mother's father had colon cancer at age 73.  Mother's brother was recently diagnosed with leukemia at age 50.  Mother's father had bone cancer at age 80.  Mother's grandmother had deep vein thrombosis in her leg in her 40s.  Mother has two half-brothers who are in good health.  Mother has an aunt on her paternal side of the family who has diabetes.  Mother has cousins on her maternal side of the family who have diabetes.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:8

**Section:** Family and Social History

**Conversation:**

```
Doctor: Are you still working, sir? 
Patient: No, I am retired now. I worked for twenty years in social security administration. 
Patient: Now I just enjoy my life with my wife, we travel a lot. I like to be extremely active. 
Doctor: That's awesome. 
Doctor: Do you drink?
Patient: Yes, but only socially. 
Doctor: How about smoking or any drugs?
Patient: No, I don't smoke or do any kind of drugs or anything. 
Doctor: Okay.
```

**Reference (calibration only):**

```
He is retired from the social security administration x 20 years.  He travels a lot and is extremely active.  He does not smoke.  He consumes alcohol socially only.  He does not use illicit drugs.  He is married.
```

**A:**

```
Family and Social History:
- Currently retired, worked for 20 years in social security administration.
- Enjoys traveling and being active.
- Drinks socially.
```

**B:**

```
He is retired.  He is a social worker.  He is a smoker.  He is a social drinker.  He denies any illicit drug use.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:10

**Section:** History of Present Illness

**Conversation:**

```
Doctor: Good afternoon, ma'am. Can you tell me more about yourself, please? 
Patient: Well, I'm seventy nine, and I'm an African American women. 
Doctor: Did the nurses get your height? 
Patient: No, they didn't. 
Doctor: How tall are you? 
Patient: I'm five foot three inches. 
Doctor: Thank you, and how much do you weigh? 
Patient: Um, I'm about one hundred ninety seven pounds. 
Doctor: Great, and do you have any major medical conditions that I should know about?
Patient: I've had type two diabetes since nineteen eighty three. 
Doctor: Thank you, and do you have any allergies to any medicine? 
Patient: No, not that I know of.
```

**Reference (calibration only):**

```
The patient is a 79-year-old African-American female with a self reported height of 5 foot 3 inches and weight of 197 pounds.  She was diagnosed with type 2 diabetes in 1983.  She is not allergic to any medicines.
```

**A:**

```
The patient is an African American woman seventy-nine years old, five foot three inches tall, and one hundred ninety-seven pounds. She has had type two diabetes since nineteen eighty three. There are no known allergies to any medicine.
```

**B:**

```
This 79-year-old African American female presents to the office for a routine checkup.  She is a 5'3" tall and weighs 197 pounds.  She has a history of type II diabetes mellitus since 1983.  She has no known drug allergies.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:14

**Section:** History of Present Illness

**Conversation:**

```
Doctor: Hello, how are you today?
Patient: I am doing well. 
Doctor: Great. What would you like to bring up today?
Patient: I have some questions about my liver. 
Doctor: Alright. Let's start with the basics. Do you drink? Excessive drinking can cause issues with the liver.
Patient: No, I do not. I take a lot of Tylenol for pain and I am worried it is effecting my liver. 
Doctor: Okay, that is a common concern. We can address that today. Do you happen to smoke?
Patient: No, I do not smoke.
```

**Reference (calibration only):**

```
Negative for use of alcohol or tobacco.
```

**A:**

```
The patient denies any alcohol use.  The patient denies any tobacco use.
```

**B:**

```
Patient: I do not smoke.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:16

**Section:** Physical Examination

**Conversation:**

```
Doctor: Did you ever see that your skin is turning blue or greyish in color?
Patient: Not that I notice. 
Doctor: Any swelling like there is water filled inside? 
Patient: Nope.
Doctor: Have you ever noticed any kind of swelling in your fingers or toes?
Patient: No.
```

**Reference (calibration only):**

```
EXTREMITIES: No cyanosis, clubbing or edema.
```

**A:**

```
Physical Examination: The patient's skin is noted to be turning blue or greyish in color, with no observed swelling. No swelling is noted in the fingers or toes.
```

**B:**

```
EXT: No cyanosis, no edema, no swelling.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:17

**Section:** Past Surgical History

**Conversation:**

```
Doctor: Any health problems or health conditions? 
Patient: No. I have never had any health issues. Other than why I am why I am her today. 
Doctor: Lucky you. No prior surgeries? 
Patient: I know right? No, I have never had any surgeries.
```

**Reference (calibration only):**

```
She has not had any prior surgeries.  Her general health has been excellent except for the above-indicated problems.
```

**A:**

```
No prior surgeries.
```

**B:**

```
None.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:23

**Section:** Allergies

**Conversation:**

```
Guest_clinician: Hello, my name is Mary. I will ask you a few questions about your medical and family history and then Doctor Smith will come and check you. Okay?
Patient: Okay. 
Guest_clinician: Do you have any other previously diagnosed medical issues?
Patient: I have sinus. I also had a stroke around two years ago.
Guest_clinician: Do you smoke or drink?
Patient: Nope, never did any of those.
Guest_clinician: Do you have any kind of allergies?
Patient: No, no known allergies.
Guest_clinician: Thank you for answering all my questions, I will let Doctor Smith know that you are ready.
```

**Reference (calibration only):**

```
The patient has sinus and CVA.  He is a nonsmoker.  No known drug allergies.
```

**A:**

```
No known allergies.  No smoking or alcohol.  No previous medical problems.  No sinus problems.  No stroke.
```

**B:**

```
Allergies: No known allergies.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:37

**Section:** Family and Social History

**Conversation:**

```
Doctor: Have you ever smoked? 
Patient: Yes, I've been smoking around one pack. 
Doctor: Each day, is it? 
Patient: Yes.
Doctor: For how long? 
Patient: Around fifteen years. 
Doctor: Do you take any other drug or consume alcohol? 
Patient: Yeah, I'm an addict. I take oxy and a few more narco stuff, which I get from the street, and I drink a lot. I need help.
```

**Reference (calibration only):**

```
polysubstance abuse. smoked 1 pack per day for 15years.
```

**A:**

```
Family and Social History:
- Smoking history: 1 pack per day for 15 years
- Substance use: Oxy and other narcotics from the street
- Alcohol consumption: Heavy drinking
```

**B:**

```
The patient is a smoker, has been smoking one pack per day for 15 years.  He is an addict and takes oxy and a few other narcotics from the street.  He drinks a lot.  He needs help.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:38

**Section:** History of Present Illness

**Conversation:**

```
Doctor: Good morning, ma'am. Did you have a good thirty-sixth birthday?
Patient: Yes, thank you. It was a nice day, despite the knee pain. 
Doctor: That's good, we'll get back to that knee in a moment. Just to confirm, you identify as white, correct? 
Patient: Yes, I do. 
Doctor: Thank you. I just needed to make sure my chart was correct. So, is this left knee still bothering you? 
Patient: Yes, unfortunately, it still is.
Doctor: You've had three Synvisc injections, correct? When was your last one?
Patient: Yes, that was about five days ago, right before my birthday. 
Doctor: Did that provide any relief at all?  
Patient: Well, I'd say there's been, um, thirty-five or forty percent improvement. 
Doctor: Are you still having the pinching pain?
Patient: Yes, it's so bad when I try to put my full weight onto this knee. 
Doctor: Can you bend this knee at all?
Patient: Ow, no, please stop. I can't handle that bending, doctor. 
Doctor: Can you straighten the knee out for me, please? 
Patient: No, not all the way, look. 
Doctor: Yes, that's not out all the way. 
Patient: It hurts really bad, doctor. 
Doctor: With ten being the worst pain ever, how would you rate your pain today out of ten?
Patient: Oh, it's easily a ten out of ten. 
Doctor: Have you used ice or heat? 
Patient: Yes, I use both. I alternate the two. 
Doctor: What medicines are you taking?
Patient: I'm using that Tylenol with codeine you gave me and then some ibuprofen I got from the grocery store. 
Doctor: Have those helped at all?
Patient: I'd say they helped pretty minimally.
```

**Reference (calibration only):**

```
This is a 36-year-old white female who presents to the office today with a complaint of left knee pain.  She is approximately five days after a third Synvisc injection.  She states that the knee is 35% to 40 % better, but continues to have a constant pinching pain when she full weight bears, cannot handle having her knee in flexion, has decreased range of motion with extension.  Rates her pain in her knee as a 10/10.  She does alternate ice and heat.  She is using Tylenol No. 3 p.r.n. and ibuprofen OTC p.r.n. with minimal relief.
```

**A:**

```
Patient: Yes, I have had three Synvisc injections, and the last one was about five days before my birthday. The knee still bothers me, and it is currently causing a pinching pain. The patient has had a 35-40% improvement from the Synvisc injections, but the pain is still a ten out of ten. The patient has not used ice or heat, and the medicines they are taking do not help much.
```

**B:**

```
The patient is a 50-year-old white female who presents today for a 36th birthday.  She has had three Synvisc injections, the last one being about 5 days prior to her birthday.  She states that she has had some improvement, but she still has some pinching pain in her left knee.  She states that she is unable to put full weight on her left knee.  She states that when she does put weight on her left knee, she has some pain.  She states that she is unable to bend her left knee.  She states that she is unable to straighten her left knee.  She states that she has a pain rating of 10/10.  She states that she uses ice and heat.  She states that she is taking Tylenol with codeine and some ibuprofen.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:42

**Section:** History of Present Illness

**Conversation:**

```
Doctor: How are you? 
Patient: I am well, I have a bad cough and some green, grey things are coming out. 
Doctor: Oh I am sorry, is it causing any shortness of breath?
Patient: No, I don't feel short of breath.
Doctor: How about fever?
Patient: No I do not have any fever.
Doctor: Any chills?
Patient: Nope.
Doctor: Okay so that's why you came to E D?
Patient: Yes I have been having this for three days and with this sputum I got scared.
Doctor: I am sorry, we can help you. How old are you?
Patient: Sure, I am sixty eight years old.
```

**Reference (calibration only):**

```
This 68-year-old man presents to the emergency department for three days of cough, claims that he has brought up some green and grayish sputum.  He says he does not feel short of breath.  He denies any fever or chills.
```

**A:**

```
Patient: I am sixty eight years old.
```

**B:**

```
The patient is a 68-year-old male who presents to the emergency room with a three-day history of productive cough and sputum production.  He denies any fever, chills, or shortness of breath.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:43

**Section:** Assessment

**Conversation:**

```
Guest_clinician: Is there any notable intra abdominal pathology? 
Doctor: None whatsoever. 
Guest_clinician: Well, that's good news.
```

**Reference (calibration only):**

```
No intra-abdominal pathology.
```

**A:**

```
None.
```

**B:**

```
Assessment: No intra-abdominal pathology noted.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:44

**Section:** Past Medical History

**Conversation:**

```
Doctor: Do you have any health conditions that I should be aware of?
Patient: Well, as you can see, I'm obese, and I also have high blood pressure. 
Doctor: Have you ever had surgery? 
Patient: Yeah, I've fractured my right knee before, and they fixed it with a pin, that was in, um, nineteen ninety. 
Doctor: Thank you, anything else you can remember?
Patient: Oh yeah, I have a history of blood clots.
```

**Reference (calibration only):**

```
High blood pressure, obesity, right patellar fracture with pin in 1990, and history of blood clots.
```

**A:**

```
Significant for obesity, hypertension, and a history of deep vein thrombosis and right knee fracture in 1990.
```

**B:**

```
Obesity, hypertension, history of knee fracture with internal fixation (pin) in 1999, history of blood clots.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:67

**Section:** History of Present Illness

**Conversation:**

```
Doctor: How old are you? 
Patient: Fifty six. 
Doctor: Are you right handed or left handed? 
Patient: I'm right handed.
Doctor: So, you have this long standing on and off lower back pain on your right side. And it all happened after your motor vehicle accident in September of two thousand and five. 
Patient: That's right. Right after accident. At that time, I did not feel anything, but five days later I started getting this abnormal like pain in the lower side of my back, especially on the right side. It kind of like moved from there to my buttocks on the posterior side on my thigh and on outside of my calf. 
Doctor: Does anything elevate your pain or decreases it? 
Patient: It gets worse when I'm sitting for a longer period, such as like driving or if I'm walking for a long period of time. It is a little less bad when walking, but still, it is there. Lying down relieves the pain for a bit and also standing helps. 
Doctor: Is there any symptom like weakness or pain in your left leg or your right leg? 
Patient: Nope. 
Doctor: Any change in your bowel movement or your urine function?
Patient: Nope. 
Doctor: Were your symptoms sudden or were they increasing gradually? 
Patient: They increased slowly. I had the pain killers, Medrol but, it has not been very effective. I also had that big injection in my back. It helped me for a few hours but then next day it was all same for me. 
Doctor: When did this happen? When did you get the injection? 
Patient: This was done four and a half weeks ago. 
Doctor: Okay, let me just quickly check your legs. They look full in strength, and they also seem symmetric to me. Can you raise your leg? Like straight up? 
Patient: Yeah sure. 
Doctor: Yeah, yes. Straight leg raising is also normal.
```

**Reference (calibration only):**

```
The patient is a 56-year-old right-handed female with longstanding intermittent right low back pain, who was involved in a motor vehicle accident in September of 2005.  At that time, she did not notice any specific injury.  Five days later, she started getting abnormal right low back pain.  At this time, it radiates into the buttocks down the posterior aspect of her thigh and into the right lateral aspect of her calf.  Symptoms are worse when sitting for any length of time, such as driving a motor vehicle.  Mild symptoms when walking for long periods of time.  Relieved by standing and lying down.  She denies any left leg symptoms or right leg weakness.  No change in bowel or bladder function.  Symptoms have slowly progressed.  She has had Medrol Dosepak and analgesics, which have not been very effective.  She underwent a spinal epidural injection, which was effective for the first few hours, but she had recurrence of the pain by the next day.  This was done four and a half weeks ago. On examination, lower extremities strength is full and symmetric.  Straight leg raising is normal.
```

**A:**

```
The patient is a 56-year-old right-handed male who has had a history of intermittent back pain on his right side.  The pain started five days after a motor vehicle accident in September 2005.  The patient states that he did not feel anything at the time of the accident, but five days later he started getting an abnormal like pain in the lower side of his back, especially on the right side.  It kind of like moved from there to his buttocks on the posterior side on his thigh and on outside of his calf.  The pain gets worse when he is sitting for a longer period of time, such as like driving or if he is walking for a long period of time.  It is a little less bad when walking, but still, it is there.  Lying down relieves the pain for a bit and also standing helps.  There is no numbness or tingling in his left leg or his right leg.  There is no change in his bowel movement or his urine function.  The symptoms started slowly and have not been very effective with the medications, Medrol and injections.  The patient states that he had the big injection in his back four and a half weeks ago.  The patient states that it helped him for a few hours but then next day it was all same for him.
```

**B:**

```
History of Present Illness:
The patient reports a long-standing on and off lower back pain on the right side, which started after a motor vehicle accident in September 2005. The pain initially occurred five days after the accident, with the location initially being the lower back, then moving to the buttocks, posterior thigh, and outside of the calf. The pain is exacerbated by prolonged sitting or walking and relieved by lying down or standing. There is no reported weakness in the left leg or any change in bowel or urinary function. The symptoms have increased gradually over time, with the patient having used pain medication and a corticosteroid injection four and a half weeks ago. The patient is able to raise their leg straight up.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:69

**Section:** Past Surgical History

**Conversation:**

```
Doctor: Have you ever had surgery, ma'am? 
Patient: What, like a joint replacement? 
Doctor: Well, it could be anything from a joint replacement to a C section.
Doctor: Oh, no. I've never had surgery. I had all of my children naturally.
```

**Reference (calibration only):**

```
None.
```

**A:**

```
None.
```

**B:**

```
None
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:83

**Section:** Review of Systems

**Conversation:**

```
Guest_clinician: I took her R O S, and everything looks normal except for mild soreness in her arm due to the vaccine.
Patient: In my left arm.
Doctor: Okay, thank you for updating the notes.
Guest_clinician: Sure, no problem.
```

**Reference (calibration only):**

```
Review of systems is otherwise negative.
```

**A:**

```
Review of Systems: 
- Mild soreness in the left arm, likely due to the vaccine.
```

**B:**

```
Review of systems is otherwise noncontributory.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:84

**Section:** Assessment

**Conversation:**

```
Doctor: How're you feeling after the Prednisone? 
Patient: Much better than before. It looks like the redness and swelling has calmed down a bit. 
Doctor: This was your first wasp sting, correct? 
Patient: Yeah, and I really hope it's my last. It definitely did a number on me.
```

**Reference (calibration only):**

```
Local reaction secondary to insect sting.
```

**A:**

```
The patient reports feeling much better after the Prednisone, with the redness and swelling subsiding. The doctor confirms it was the patient's first wasp sting, and the patient expresses hope that it is their last.
```

**B:**

```
1.  Prednisone. 2.  Redness and swelling.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:89

**Section:** Family and Social History

**Conversation:**

```
Doctor: I just need a few pieces of background information, before we get started. 
Patient: Absolutely, doctor. 
Doctor: What do you do for a living, sir? 
Patient: Actually, right now I'm on disability. 
Doctor: Okay, and do you drink or smoke?
Patient: No, doctor. I don't do either of those. 
Doctor: Good, are you married?
Patient: Not married yet, but I've been dating my girlfriend for a while now. 
Doctor: Do you two live together? 
Patient: Yes, doctor, we do.
Doctor: How would you describe your activity level day to day?
Patient: Do you mean like exercise?
Doctor: Well, anything from bathing, dressing, feeding, etc. We call these activities of daily living, how would you rate that?
Patient: To be honest with you doctor, I'd have to say it's minimal. My girlfriend has to help me with most of it right now. 
Doctor: Okay, and do you remember when you had your last drug test?
Patient: No, doctor. I really can't remember.
```

**Reference (calibration only):**

```
Thee patient is on disability.  He does not smoke.  He does not drink alcohol.  He is single.  He lives with a girlfriend.  He has minimal activities of daily living.  The patient cannot recollect when last a urine drug screen was done.
```

**A:**

```
He is a disabled gentleman who does not smoke or drink.  He is dating a girlfriend.  He lives with her.  He has minimal ADLs.
```

**B:**

```
Marital Status: Married. Living together. Activity Level: Minimal. Last Drug Test: Not applicable.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:108

**Section:** Assessment

**Conversation:**

```
Doctor: How's she doing today? 
Guest_family: She's been blowing up green snot and complaing of ear pain. 
Doctor: Both ears? 
Guest_family: Both the right and left. 
Doctor: How long has she been bringing up green snot? 
Guest_family: Maybe six or so days? 
Doctor: Let's see. It looks like she may have sinusitis. After checking both ears, I noticed fluid buildup in the right middle ear. I'll go ahead and prescribe her some antibiotics and hopefully she'll be as good as new in a few days. I'd like her to come back for a follow up to make sure all the fluid in her ear is gone.
```

**Reference (calibration only):**

```
Ongoing purulent rhinitis.  Probable sinusitis and serous otitis.
```

**A:**

```
1.  Possible sinusitis. 2.  Possible ear infection.
```

**B:**

```
Assessment: The patient is experiencing symptoms of sinusitis, including green snot and ear pain. There is fluid buildup in the right middle ear. The patient is prescribed antibiotics and should return for a follow-up to ensure the fluid is cleared.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:115

**Section:** Chief Complaint

**Conversation:**

```
Doctor: So what brings you in today? 
Patient: Um I think I'm due for a checkup. While I'm here, I also wanted to figure out why I'm having so much joint pain all over. 
Doctor: When did you first notice the pain? 
Patient: It's been a couple weeks now. I thought it'd go away on its own. I've taken Advil for it, which helps a tiny bit.
```

**Reference (calibration only):**

```
Joints are hurting all over and checkup.
```

**A:**

```
Chief Complaint: Joint pain, with the onset of symptoms being a couple weeks ago, affecting multiple joints.
```

**B:**

```
Joint pain.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:127

**Section:** History of Present Illness

**Conversation:**

```
Doctor: We have placed this nasogastric tube for decompression.
Guest_family: Okay.
Doctor: How are you feeling now?
Patient: Um.
Guest_family: She said that she feels better now.
```

**Reference (calibration only):**

```
The patient has NG tube in place for decompression.  She says she is feeling a bit better.
```

**A:**

```
Patient: I feel better now.
```

**B:**

```
The patient is in stable condition.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:134

**Section:** Medications

**Conversation:**

```
Doctor: What are you taking? 
Patient: You mean meds?
Doctor: Yes, sir.
Patient: Actually, that nurse asked me already and reviewed it with me. Do you want me to tell you again?
Doctor: No let me check the chart then.
Patient: Okay.
Doctor: You are not on any blood thinners right?
Patient: No I am not.
Doctor: Okay great.
Patient: Yeah.
```

**Reference (calibration only):**

```
He is currently on several medications, a list of which is attached to the chart, and was reviewed.  He is not on any blood thinners.
```

**A:**

```
Medications: None noted.
```

**B:**

```
None.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:146

**Section:** History of Present Illness

**Conversation:**

```
Doctor: Good morning, young man. Is this your mother?
Patient: Yes, doctor.
Doctor: Good, nice to mee you. Can you tell me more about your son, please? 
Guest_family: Good morning to you too, doctor. Well, he's about five and a half now, and he broke both the bones in his forearm in September of two thousand seven. 
Doctor: How did the fracture heal? Generally, children heal very well. 
Guest_family: Well, yes, until he also rebroke it about a month ago. 
Doctor: Yes, I see now, there's an ulnar nail pretty prominently visible under the skin, did he have surgery for this? 
Guest_family: Yes, about a month ago now. Should we remove the nail?
Doctor: We'll have to, even though its early.
Guest_family: What will we do after the nail is removed? 
Doctor: After that, we'll put him back in a cast for about another three weeks. We'll evaluate him and see how he's doing.  
Guest_family: Okay. What are the risks of infection for this surgery?
Doctor: The risk of infection is overall very low, honestly its less than one percent. We use antibiotics to control for infection the entire time. Other risks include bleeding, changes in sensation in most of the extremity, or need for longer casting. I would not worry too much about these risks. I have not seen anything bad happen before.
Guest_family_1: Will he be asleep for the surgery?
Doctor: Yes, he won't feel a thing.
```

**Reference (calibration only):**

```
The patient is a 5-year, 5-month-old male who sustained a both-bone forearm fracture in September 2007.  The fracture healed uneventfully, but then the patient subsequently suffered a refracture one month ago.  The patient had shortening in arms, noted in both bones.  The parents opted for surgical stabilization with nailing.  This was performed one month ago on return visit.  His ulnar nail was quite prominent underneath the skin.  It was decided to remove the ulnar nail early and place the patient in another cast for 3 weeks. Risks and benefits of the surgery were discussed with the mother.  Risk of surgery incudes risks of anesthesia, infection, bleeding, changes in sensation in most of the extremity, need for longer casting.  All questions were answered and mother agreed to above plan.
```

**A:**

```
The patient sustained a fracture of both the bones in his forearm in September 2007. He underwent surgery for a broken ulnar nail in the same month. The fracture healed well initially but re-fractured approximately a month later. The patient underwent surgery to remove the nail, and a cast will be applied for approximately three weeks post-surgery. The risks of infection, bleeding, and changes in sensation are low, but the patient will be asleep during the surgery.
```

**B:**

```
The patient is a 5-year-old male who was seen in the emergency room in September 2007 for a closed fracture of the left forearm.  The patient was treated with closed reduction and cast.  The patient was seen in the emergency room again in October 2007 for a closed fracture of the left forearm.  The patient was treated with closed reduction and cast.  The patient was seen in the emergency room again in November 2007 for a closed fracture of the left forearm.  The patient was treated with closed reduction and cast.  The patient was seen in the emergency room again in December 2007 for a closed fracture of the left forearm.  The patient was treated with closed reduction and cast.  The patient was seen in the emergency room again in January 2008 for a closed fracture of the left forearm.  The patient was treated with closed reduction and cast.  The patient was seen in the emergency room again in February 2008 for a closed fracture of the left forearm.  The patient was treated with closed reduction and cast.  The patient was seen in the emergency room again in March 2008 for a closed fracture of the left forearm.  The patient was treated with closed reduction and cast.  The patient was seen in the emergency room again in April 2008 for a closed fracture of the left forearm.  The patient was treated with closed reduction and cast.  The patient was seen in the emergency room again in May 2008 for
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:149

**Section:** Family and Social History

**Conversation:**

```
Doctor: Are you aware of any medical issues running in your family?
Patient: Well, my mom died of a stroke. She was in her late fifties. My dad had some heart issues. He also had high blood pressure.
Doctor: Do you smoke? 
Patient: I was a heavy smoker before many years ago, but then I quit in nineteen ninety.
Doctor: How much would you use to smoke before? 
Patient: Around two to three packs per day. 
Doctor: What did you used to do for a living? 
Patient: I've been a feed salesman almost throughout my adulthood.
```

**Reference (calibration only):**

```
Mother died of a stroke at age 58. Father had CAD and HTN. The patient quit smoking in 1991, but was a heavy smoker (2-3ppd) for many years. He had been a feed salesman all of his adult life.
```

**A:**

```
Family and Social History:
- Family history: Stroke in the patient's mother, heart issues in the patient's father.
- Smoking history: Heavy smoker for many years, quit smoking in the past.
- Occupation: Feed salesman.
```

**B:**

```
Mother died of stroke in her 50s.  Father had some heart issues and had hypertension.  He died in his 70s.  He was a heavy smoker, used to smoke 2-3 packs per day.  He was a feed salesman.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:156

**Section:** Past Surgical History

**Conversation:**

```
Doctor: Have you ever had surgery in the past? 
Patient: No, not that I know of.
Doctor: So, there's no history of gallbladder or appendix removal, or joint replacements?
Doctor: No, I've never had any of that done.
```

**Reference (calibration only):**

```
None.
```

**A:**

```
No known past surgical history.
```

**B:**

```
None
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:158

**Section:** Imaging

**Conversation:**

```
Doctor: So, I am looking at your x ray here.
Patient: Oh yes please tell me if everything is fine.
Doctor: Yes so, we have a two view of you shoulder. I am not seeing any bone abnormalities or any degenerative changes, so no wear and tear.
Patient: Is that normal?
Doctor: Yes, it is normal.
Patient: That's good.
```

**Reference (calibration only):**

```
Two view x-rays were taken of the shoulder.  There are no osseous abnormalities or significant degenerative changes.
```

**A:**

```
Imaging: X-ray of the shoulder shows two views. No bone abnormalities or degenerative changes are noted.
```

**B:**

```
Shoulder x-ray.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:172

**Section:** Family and Social History

**Conversation:**

```
Doctor: Do you like to travel?
Patient: I do. In fact, I have been to more than six countries.
Doctor: Have you travelled outside the country recently?
Patient: No not recently, it's been couple years now, but I plan to.
Doctor: That's great.
Patient: Yeah.
```

**Reference (calibration only):**

```
Denies any recent travel overseas
```

**A:**

```
Family and Social History:
The patient has traveled to more than six countries and plans to travel again in the future.
```

**B:**

```
She has travelled to more than six countries.  She has not travelled outside the country recently.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:173

**Section:** Review of Systems

**Conversation:**

```
Doctor: Any chest pain or shortness of breath?
Patient: No chest pain, but I tend to have shortness of breath after any type of exertion.
Doctor: How about bladder and bowel issues?
Patient: No, that is fine.
Doctor: Any excessive or unstoppable bleeding issues?
Patient: No, I do not have any bleeding issues.
Doctor: Oh.
Patient: Yeah.
```

**Reference (calibration only):**

```
He denies any chest pain.  He does admit to exertional shortness of breath.  He denies any GI or GU problems.  He denies any bleeding disorders.
```

**A:**

```
Review of Systems:
- No chest pain
- Shortness of breath after exertion
- No bladder or bowel issues
- No excessive or unstoppable bleeding issues
```

**B:**

```
Bowel/bladder, no dysuria or hematuria.  No chest pain.  No shortness of breath.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:189

**Section:** Medications

**Conversation:**

```
Doctor: What medications are you taking currently? 
Patient: I take Synthroid for my low thyroid and I used to take Aspirin, but I stopped that about a week ago.  
Doctor: I see. And you're no longer taking Terazosin, Lisinopril, or Atenolol? 
Patient: Yeah. My cardiologist, Doctor X, told me to stop taking them weeks ago.
```

**Reference (calibration only):**

```
The patient takes Synthroid and aspirin.  Aspirin had been discontinued about 1 week ago.  He used to be on atenolol, lisinopril, and terazosin, both of which have been discontinued by his cardiologist, Dr. X several months ago.
```

**A:**

```
Medications: Synthroid for thyroid, Aspirin (stopped about a week ago), Terazosin (stopped weeks ago), Lisinopril (stopped weeks ago), Atenolol (stopped weeks ago).
```

**B:**

```
Synthroid, Aspirin, Terazosin, Lisinopril, and Atenolol.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 


## Pair test1:192

**Section:** Assessment

**Conversation:**

```
Doctor: How has she been since the last time we saw you both?  
Guest_family: She has been in good spirits.  She has so much energy. She has had some constipation issues lately.  
Doctor: How has her breathing been? Any changes?  
Guest_family: No. Everything is the same.  
Doctor: According to her chart she has not gained any weight since her last visit. I am sure it is due to her high energy level, but it is something we need to keep a close eye on.  
Guest_family: What can I do to help her gain weight? 
Doctor: I would like you to focus on making sure she is getting enough protein in her daily diet. Here is a handout on meal suggestions and tips for keeping meal times on a consistent schedule.  
Guest_family: Thank you.
```

**Reference (calibration only):**

```
A 2-year-old with chronic lung disease, doing the sprints, some bowel difficulties, also just weight gain issues because of the high-energy expenditure with the sprints that she is doing.
```

**A:**

```
Assessment: The patient has been in good spirits and has high energy levels. She has experienced some constipation issues. Her breathing is normal, and there have been no changes. She has not gained any weight since her last visit, and the doctor suggests focusing on protein intake in her diet and maintaining meal times on a consistent schedule.
```

**B:**

```
1.  The patient is in good spirits. 2.  The patient has had some constipation issues. 3.  The patient's breathing is unchanged. 4.  The patient has not gained any weight since her last visit. 5.  The patient's energy level is high.
```

SCORES: A _ _ _ _ | B _ _ _ _ | PREF: _ | REASON: 
