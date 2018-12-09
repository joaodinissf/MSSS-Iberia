# Modeling and Simulation of Social Systems Fall 2018
(text between brackets to be removed)

> * Group Name: Iberia
> * Group participants names: Miguel Perez Sanchis, Joao Dinis Sanches Ferreira
> * Project Title: Group performance and division of labour in an environment with different personalities
> * Programming language: Python 3

## General Introduction

### Topic
We address the topic of division of labour (also called task allocation) and group performance (how long agents take to perform such tasks) using an agent-based model. We include three dimensions in the agents: expertise, motivation, and mood. These will determine how they interact with each other to allocate the tasks, as well as how they perform. We also include an attribute for the agents: the Myers-Briggs Type Indicator (MBTI). This links two research topics (group performance and psychologic-types theory) into one project.

This topic is fundamental in order to better understand and improve human interactions. We know that the performance of a group of people can be much more than the sum of its parts, and this is only possible if there are valuable interactions between the people. It also connects with the problem of "hiring" or "group performance" in different situations.

In a nutshell, we want to see how people interact and perform when they have different sets of tasks to do.

### Goal
Our main goal was to fully understand, reproduce and expand an existing simulator. We want to have an adaptable and easy-to-modify code. 


## The Model
To put it simple, our simulator basically consists on four key steps that determine how agents interact and what is their performance. They are the following:
1. Interaction: agents try to convince each other that themselves (or others) have to do a certain task that has to be allocated. This interaction depends on their expertise, motivation and mood.
2. Frustration update: after these interactions, the mood of the agents is updated depending on the agents they have interacted with, as well as how fast they reached an agreement on who does what task.
3. Performance: agents then performs the actions they have been allocated, and the time they take to complete the tasks depends again on the expertise and motivation they have for each of the skills the task is made of, as well as their level of frustration or mood.
4. After they complete this process, their motivation and expertise is also updated.

We are aware that this is a very simplified way of modeling human interactions. It is, however, also easy to interpret. We had always in mind Bonini's paradox: "As a model of a complex system becomes more complete, it becomes less understandable. Alternatively, as a model grows more realistic, it also becomes just as difficult to understand as the real-world processes it represents" (see [1]).

## Fundamental Questions
1. Our primary focus is to determine the evolution of a group's performance over time depending on relationships of individuals in the group-based on MBTI- and task variety (a concept developed in [6]) which refers to how many different skills are needed in order to carry out a given set of tasks)

2. In addition, we want to see the evolution of "mood" or "frustration", which is the additional dimension we incorporated to the simulator we used, as agents interact. This variable indicates how comfortable a person is regarding the work environment and inter-personal relationships.

3. As a secondary goal, we would like to tweak some of the existing parameters of the model- mainly expertise and motivation- to see how this affects the new simulator.


## Expected Results

1. In an environment with high task variety, we are expecting similar results both when there are "good" and "bad" inter-personal relationships. We only expect a different order of magnitude in the performance time, but with similar variations. This is because agents will have to adapt to new tasks with different skills and their allocation time will take longer due to discussions caused by the bad relationship (for more details see report- "model" section).

2. When task variety is low, however, we expect the performance time curve to decrease faster when agents have a good relationships. The reasoning behind this is that a better relationship will lead to quickest decisions made regarding task allocation and they will be in a better mood so their performance will be better.

We were also interested in replicating all the results found in [6] in order to verify we were following the same path as the previous researchers.


## References 
1.    J.M. Dutton and W.H. Starbuck.
Computer simulation of human behavior. Wiley series in management and administration. Wiley, 1971. isbn: 9780471228509.

2.   NERIS Analytics Limited. 16personalities.com - Personality Test. https://www.16personalities.com/

3.    Radu Ogarca, Liviu Craciun, and Laurentiu Mihai. “The influence of the behavioral profile upon the management team’s performance.” In: Annals of the University of Craiova, Economic Sciences Series 1 (2015).

4.    Robert E Wood. “Task complexity: Definition of the construct”. In: Organizational behavior and human decision processes 37.1 (1986), pp. 60–82.

5.    Lianying Zhang and Xiang Zhang. “Multi-objective team formation optimization for new product development”. In: Computers & Industrial Engineering 64.3 (2013), pp. 804–811.

6.    Kees Zoethout, Wander Jager, and Eric Molleman. “Formalizing self-organizing processes of task allocation”. In: Simulation Modelling Practice and Theory 14.4 (2006), pp. 342–359.

7.    Kees  Zoethout,  Wander  Jager,  and  Eric  Molleman.  “Task dynamics  in  selforganising task groups: expertise, motivational, and performance differences of specialists and generalists”. In: Autonomous Agents and Multi-Agent Systems 16.1 (2008), pp. 75–94

## Research Methods
Agent-Based Model.

## Other
Please read the report for a more complete explanation of the project, its goals, motivations and implementation. We did not want to have not useful information in this readme file.

# Reproducibility

(step by step instructions to reproduce your results. *Keep in mind that people reading this should accomplish to reproduce your work within 10 minutes. It needs to be self-contained and easy to use*. e.g. git clone URL_PROY; cd URL_PROY; python3 main.py --light_test (#--light test runs in less than 5minutes with up to date hardware)) 

