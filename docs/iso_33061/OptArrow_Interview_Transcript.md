# OptArrow: V6.4 Audit Interview Transcript

**Date:** September 30, 2026  
**Interviewees:** Farid Zare (ZF) - Core Developer, Zaffar Haider Janjua (ZJ) - Supervisor  
**Interviewer:** Oluwatimilehin Ayomide Oladipo (OO)  

***

**OO [0:06]:** OK. OK.

**ZJ [0:08]:** I think we can discuss these questions now, but still let's give Farid time to properly, you know, like maybe he can give you a written response later. What do you think? I mean, we can still present to him and let's see. But probably, you know, some things need some time, so let's present it. That's fine, yeah.

**OO [0:32]:** Investing, yeah.

**ZJ [0:35]:** And I can also download it so that I can take notes.

**ZF [0:39]:** I'm just quickly reading the questions. Some of them I can answer right away. I need some time to get back to you.

**OO [0:39]:** So.

**ZJ [0:49]:** Yeah, yeah, just, yeah, yeah.

**OO [0:52]:** Okay. So good afternoon, Farid. Good afternoon Zaffar. So the idea of these questions is that based on the processes that we've been able to document, which would include the requirements, the architecture, and the design processes... One of the outputs of each of those processes is like an evidence matrix. So what that means is just like a mini gap analysis that shows up the best practices that we were able to achieve and the evidences that we used to achieve those best practices, and the base practices that we're not able to achieve and the evidences that are missing. So the idea of these questions is to be able to get your perspective, which will be the most relevant perspective on evidences that are missing or that are not complete. 

**OO [1:50]:** This also will be added to the evidence pool to be able to generate a much more high-level documentation. So I have the question sectioned into three phases. We have the requirement phase, which will be TEC.3, and TEC.4, and then TEC.5. I will just ask the question and you just go ahead and answer, and then I will transcribe it after. 

**OO [2:11]:** So for the requirement definition, the question seeks to understand how the feedback is reviewed and how traceability is maintained. This basically focuses around stakeholders' requirements. So the stakeholder feedback and review... it says here that our code analysis shows strong implementation of requirements, but how do we currently gather, number one, and review the feedback from stakeholders? Like data scientists, researchers, which would be our users.

**ZF [2:49]:** GitHub issues, GitHub issues. GitHub issues are the ways that people can make feedback. Does that make sense?

**OO [3:04]:** I can't hear you properly. That's why I'm a bit confused.

**ZJ [3:12]:** I mean, I can hear you, but...

**ZF [3:14]:** Can you hear me?

**ZJ [3:16]:** Yeah, yeah, I can hear you. Can you hear it?

**ZF [3:17]:** Yes, so for feedback. Can you hear me?

**OO [3:22]:** Yeah, I can hear you now. So is there a formal process for reviewing the needs of the stakeholders and their feedback on the requirements?

**ZJ [3:24]:** OK.

**ZF [3:32]:** So feedbacks are gathered using the GitHub issue, like the project's GitHub. People can make issues, but we don't have any traceability like agreement. These are very sophisticated. Maybe we should, maybe we should, but like we don't have the, for example, I think technological alternative. For example, some of the decisions were made because the PI wanted to build this this way. And the students, they went on, for example, PI wanted IPC transport layer, for example. And the students went on and built it. So does that mean that, I don't know, like alternatives were not considered or it was a personal choice? I don't know. I don't know how that would fit in your system.

**OO [4:31]:** Okay. Okay, so...

**ZJ [4:35]:** Yeah, and if I can add a few things here, you know, Ayomide, these things are not yet formalised in my understanding. That's the purpose we are working on. We try to guide Farid how to formalise these things. So, you understanding my point?

**OO [4:50]:** So that's the main reason. So I understand the majority of those things are still ongoing. So we can also put on an hypothetical cap here and say, hypothetically, how would an ideal situation look like if we're going to implement this? How would a stakeholder feedback, how would that be reviewed in your own best understanding on how this project is going to scale?

**ZF [5:21]:** [Inaudible / Mehmood].

**ZJ [5:22]:** I, I... Yeah, sorry, I'm interrupting again, but in my understanding, this is a matter of research, like how normally this type of projects generate their feedbacks and maintain it. And you can add it as a note. So what I'm trying to say, whatever practice they are doing, that's fine. You can just note through this question and answer session. That's perfectly all right. But what I'm trying to say is that my understanding the process is still not mature and for the rest of the practices is still not mature because it's just a research project, and normally there is the established processes with the, for example, having commercial projects or stable projects, right? The understanding is it's a small project.

**ZJ [6:16]:** We are aiming to convert this into an established project, where we can just define all these processes, and here, probably... I would say your research is important in these areas, Ayomide, rather than what practices Farid is using. But you can also include his response. That's perfectly all right. You're understanding my point?

**OO [6:40]:** Yeah, yeah, I do.

**ZJ [6:42]:** Like just investigating other projects how they normally do it. And that can actually add knowledge, you know, so that, in other words, educate us, like, okay, in other projects, while using best practices, we maintain stakeholder feedback in this way and that way and so on, right? So we even generate a report and Farid read that report, you know, so he can just understand like what's the best practice to achieve this thing. That's our purpose.

**OO [7:16]:** Okay, so those suggestions for this research, which will build into making this a much established project, are those allowed to be put into evidence pool for the process documentation or just for writing purpose only?

**ZJ [7:17]:** Yeah. I don't understand your question.

**OO [7:38]:** So for example, if we do a research and we say, okay, this is like the industry standard of doing something, can that be accepted into the evidence pool? Or we're just writing it as just a research writing?

**ZJ [7:53]:** No, yeah, okay, now I understand, okay, so if you, yeah, so for the possibility, you know, if you think like, of course you are doing this question answer session, okay, so this could serve as a basic evidence. But what I'm trying to say that my understanding is that because it's just a small project. So probably they don't have mature processes to achieve whatever for traceability and so on, right? Initial guess we can get through this interview. Let's say question as a session. We can quote that, but then you can say that this is partially satisfied or totally missing. Let's say.

**ZJ [8:40]:** And in your document, because your thesis is more about what you say, not gap analysis, but to refine the documentation, isn't it? Like according to the base practice. So you can just give us some suggestions as well under that. That instead of, for example, the best practice they are doing, they can improve their documentation process by following these easy steps. You can also give a reference to a commercial project or a standard, how they tell you. So that's all about the information coming from your side will educate us. You understanding my point? That's the idea of the project.

**OO [9:20]:** Yeah. Okay.

**OO [11:09]:** OK. So, we'll move to the architectural definition. So, this question seeks to specifically understand how the architectural decisions were evaluated, how they were mapped, and how they were governed in terms of traceability. So, best practice one says that we need to prepare for architectural definition. So did we outline a formal architectural strategy or roadmap before building OptArrow or did the architecture just evolve organically as we built it?

**ZF [11:44]:** Yeah, I think the second one, it evolved as we went on. Frankly, in this sort of research project is usually the case that people, the developers, it can be the PI or other developers, they have some past experiences working with different tools or working on different projects and they have difficulties in those projects. Or they gained some experience in those projects that it made them to the conclusion that maybe we should try this tool, maybe we should come up with this decision for this new tool. But [not] like a well-documented process for that.

**OO [12:34]:** Okay, thank you. That's a good answer. So we see that the final architecture uses Apache Arrow Flight. And so what was the rationale behind selecting this specific framework? And what specific architectural concern drove these choices?

**ZF [12:54]:** Yeah, so Apache Arrow, because it's in-memory, it's in-memory data transfer. That's one of the different. The other one is that it's compatibility with different languages, so it's multilingual. And you can basically transfer data from one language to the other language of choice.

**OO [13:19]:** OK.

**ZF [13:19]:** So yeah, these are the choices for Apache Arrow. Is it, was it four or was it?

**OO [13:25]:** Correct.

**ZJ [13:30]:** Four.

**ZF [13:31]:** Yeah, also HiGHS... also HiGHS because it's an open source and free solver.

**OO [13:39]:** Okay.

**ZF [13:39]:** It is usually one of the popular solvers that the developers and in science, they did choose HiGHS because it's free and it's open source.

**ZJ [13:44]:** Yeah.

**OO [13:50]:** Alright. Okay, thank you for that. And also, the 5th question would be assessing other candidates in terms of decisions about architecture decision. So during the design phase, did you model or consider alternative architectural candidates? How did you compare them and why was the current architecture [chosen]? I think you answered that already, but maybe if you could talk a little bit about if other architecture were considered.

**ZF [14:24]:** Yes, so the previous architecture that we were using was Cobra Toolbox. Basically, the Cobra Toolbox, you have the model and the solver in the same working station, basically, you have your PC or your laptop and install it on your laptop and you have your code there and you solve your mathematical problem on your laptop. But then we figured out maybe that's not the best architecture that we can do for our analysis. Maybe it's best to do the mathematical optimization on a remote server, but have our code on our working laptops or PCs. And the reason for that was that a developer could still work with their PC or laptop.

**OO [15:09]:** Yeah.

**ZJ [19:15]:** accepts or rejects any formal changes in the architecture, right? That's the governance control. And then, because it's making future changes to OptArrow or... is evolution managed informally by the core developers and so on. Okay, so maybe here I think hierarchy. It's good to add hierarchy and if they are following any process-based approach. Yeah, thank you.

**ZF [19:44]:** Yeah, no, I don't think that we have such a very well set up process approach at the moment.

**ZJ [19:52]:** Okay.

**ZF [19:56]:** Would you like me, like, are you asking me to develop that or is it more like that Ayomide will come up with suggestions for improvement?

**ZJ [20:03]:** No, no, no, I can get this, this page. Yeah, we are just monitoring your processes, okay? So whatever is missing, so the purpose is like, we can then suggest you how to fix up these things.

**ZF [20:11]:** Okay, great.

**OO [20:19]:** Yeah, I'll do that. I'll do that.

**ZJ [20:21]:** there and then he give write some kind of suggestions using whatever analysis he do and then based or whatever.

**OO [20:31]:** Yeah, I'll definitely do that. Thank you. And then the last aspect is the design definition. So this is now the aspect, the process that helps us to map the architecture to actual implementation of codes. And we have strong evidence in terms of the design itself, the code is very, very mature. And the question is basically to strengthen our understanding on how alternative systems were evaluated. So in terms of assessing technology or alternatives when developing is being made. So when designing the specific system element, like the IPC transport layer. Did you evaluate any alternative libraries or technology besides Apache Arrow? I think you mentioned something in regards to Cobra toolbox and I guess I'm not sure. And then how were those alternative assessed before you commit to the final design?

**ZF [21:32]:** Yeah, so for the Apache data type. Um... We didn't try any alternative. We actually didn't find any alternative. Let me see if there is any alternative to me. For Apache, um. We didn't try any other protocol for data transfer and data storage between the package. Um... But for the process design, we tried different things and some of them we... We did, we left them and we dropped them in the middle of the development because they were not working well. I don't have, because I'm not working on that for probably a couple of months. I don't have anything on from the top of my head, but if we go through the GitHub comment on the repository, we can see that there were some feature developed, changed, modified, deleted from the project. And I would call them as alternative routes that we went and sometimes it didn't work, they were not working well. Um, and we replaced it with other methods. Okay.

**OO [32:47]:** And also the diagram you asked me to, I'm making it on draw.io now, so I've not finished that or I'll have it before next meeting.

**ZJ [33:01]:** Yeah, that's very important because whatever diagram you make, there's a lot of logical mistakes, to be honest, the diagram you presented earlier. So let's fix them, okay?

**OO [33:13]:** Yep, thank you.

**ZJ [33:16]:** OK, guys, then see you later.

**OO [33:17]:** Thanks, Farid. Thanks, Zaffar.

**ZF [33:18]:** Have a nice day, yeah, bye.

**ZJ [33:19]:** Bye-bye. Thank you. You too.
