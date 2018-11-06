import classes/agent.py
import classes/skill.py
import classes/task.py
import classes/workplace.py

def main():
    Workplace my_workplace()

    my_workplace.add_agent(
    Agent(
        [Skill(0), Skill()]
    ))

    my_workplace.add_agent(Agent())

    my_workplace.add_task(Task())
    my_workplace.add_task(Task())
    my_workplace.add_task(Task())

    my_workplace.process_tasks()

if __name__ == "__main__":
    main()
