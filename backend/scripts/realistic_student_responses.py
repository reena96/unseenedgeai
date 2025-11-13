"""
Realistic student response templates for enhanced seed data generation.

These responses are designed to reflect authentic K-8 student language patterns
across different grade levels, skill levels, and soft skill domains.

Based on research of:
- ClassBank classroom transcripts
- Educational psychology literature
- Age-appropriate vocabulary standards
- Real student speech patterns
"""

# Empathy-focused responses
EMPATHY_RESPONSES = {
    "high": [
        # Grade 2-3
        "I saw my friend was sad because they couldn't find their pencil, so I gave them one of mine.",
        "When Tommy fell down at recess, I helped him up and asked if he was okay.",
        "My partner didn't understand the math problem, so I showed them how I figured it out step by step.",
        # Grade 4-5
        "I noticed that Maya was sitting alone at lunch, so I invited her to sit with our group. She seemed really happy about it.",
        "During group work, Alex was having trouble with the assignment. Instead of rushing ahead, I took time to explain it in a different way that made sense to them.",
        "My little brother was frustrated with his homework, so I helped him understand it without just giving him the answers.",
        # Grade 6-8
        "I realized my friend was going through a difficult time at home, so I made sure to check in with them and let them know I was there to listen if they needed to talk.",
        "In our science project, one team member was struggling with their part. I offered to help them brainstorm ideas and work through the challenging sections together.",
        "I noticed a classmate being excluded from activities, so I made an effort to include them and encouraged others to do the same. Everyone deserves to feel welcome.",
    ],
    "medium": [
        # Grade 2-3
        "I shared my crayons with someone who forgot theirs.",
        "When my friend was upset, I tried to make them feel better.",
        "I helped clean up even though it wasn't my mess because I wanted to help the teacher.",
        # Grade 4-5
        "I worked with a new student on a project and made sure they understood what we were doing.",
        "My teammate made a mistake in the game, and I told them it was okay and we'd do better next time.",
        "I listened to my friend talk about their pet that was sick and told them I hoped it would feel better.",
        # Grade 6-8
        "I helped my lab partner when they didn't understand the experiment we were doing.",
        "I noticed someone sitting alone and asked if they wanted to join our group for the activity.",
        "When my friend was stressed about the test, I reminded them that they had studied hard and would do fine.",
    ],
    "developing": [
        # Grade 2-3
        "I played with my friend at recess.",
        "I said sorry when I bumped into someone.",
        "I helped pass out papers for the teacher.",
        # Grade 4-5
        "I let someone borrow my eraser.",
        "I worked with my group on the project.",
        "I helped someone find their classroom.",
        # Grade 6-8
        "I worked with my partner on the assignment.",
        "I helped carry books to the library.",
        "I said thank you when someone helped me.",
    ],
}

# Problem-solving responses
PROBLEM_SOLVING_RESPONSES = {
    "high": [
        # Grade 2-3
        "When I couldn't find my library book, I thought about where I last saw it. I checked my backpack, then my desk, and finally found it in my cubby!",
        "The puzzle piece didn't fit at first, so I tried turning it different ways until I found the right spot.",
        "I didn't know how to spell a word, so I sounded it out slowly and then checked it in the dictionary.",
        # Grade 4-5
        "Our group project wasn't working because everyone had different ideas. I suggested we write down all the ideas, then vote on the best parts of each one to combine them.",
        "I was stuck on a math problem, so I broke it down into smaller steps and worked through each part separately until I understood how to solve it.",
        "When our science experiment didn't work the first time, I reviewed our procedure, found where we made a mistake, and we tried again with the correct method.",
        # Grade 6-8
        "I encountered a complex coding error in my program. I systematically debugged each section, used print statements to track variable values, and eventually identified the logic error in my conditional statement.",
        "Our debate team had conflicting evidence. I organized all our sources, cross-referenced the data, identified the most credible information, and created a coherent argument structure.",
        "When multiple approaches to the geometry proof seemed valid, I worked backwards from the conclusion, tested each hypothesis, and eliminated impossible paths until I found the elegant solution.",
    ],
    "medium": [
        # Grade 2-3
        "I couldn't reach the book on the high shelf, so I got a step stool.",
        "When I didn't understand the directions, I asked the teacher to explain again.",
        "My pencil broke, so I sharpened it and kept working.",
        # Grade 4-5
        "I forgot my calculator, so I used paper and pencil to do the math instead.",
        "When I got stuck on the reading questions, I went back and read that part of the story again.",
        "Our group couldn't agree, so I suggested we try it both ways and see which worked better.",
        # Grade 6-8
        "I didn't understand the history assignment, so I looked up extra information online to help me.",
        "When the experiment results weren't what we expected, we checked our measurements and tried again.",
        "I had trouble with the essay structure, so I made an outline first to organize my thoughts.",
    ],
    "developing": [
        # Grade 2-3
        "I asked for help when I didn't know what to do.",
        "I tried again when it didn't work the first time.",
        "I looked at the example to see how to do it.",
        # Grade 4-5
        "I used the notes to help me remember.",
        "I worked with a partner to figure it out.",
        "I checked my answer to make sure it was right.",
        # Grade 6-8
        "I looked at my notes to find the answer.",
        "I asked my friend how they did it.",
        "I tried a different way when the first way didn't work.",
    ],
}

# Self-regulation responses
SELF_REGULATION_RESPONSES = {
    "high": [
        # Grade 2-3
        "I was getting frustrated with my drawing, so I took three deep breaths and started fresh with a new paper.",
        "When I wanted to play instead of finishing my work, I reminded myself that I could play after I was done.",
        "I was upset about losing the game, but I congratulated the other team because I know they played well.",
        # Grade 4-5
        "I caught myself getting distracted during independent reading. I closed my eyes for a moment, refocused on my book, and set a goal to finish the chapter before taking a break.",
        "When I received a lower grade than expected, I felt disappointed but I talked to my teacher about what I could improve instead of giving up.",
        "I noticed I was rushing through my homework and making careless mistakes, so I slowed down and checked each answer carefully.",
        # Grade 6-8
        "During the test, I felt my anxiety rising. I paused, used my breathing techniques, reminded myself that I had prepared well, and approached each question methodically.",
        "I was frustrated with my essay draft, but instead of crumpling it up, I took a break, came back with fresh perspective, and revised it constructively.",
        "When my project partner wasn't pulling their weight, I felt annoyed but chose to have a calm conversation about expectations rather than reacting emotionally.",
    ],
    "medium": [
        # Grade 2-3
        "I wanted to talk, but I remembered to raise my hand and wait my turn.",
        "I was mad, but I used my words instead of yelling.",
        "I took a break when I started feeling upset.",
        # Grade 4-5
        "I was getting frustrated, so I took a few minutes to calm down before continuing.",
        "I reminded myself to focus on my own work instead of getting distracted.",
        "When I didn't do well on the quiz, I decided to study more for the next one.",
        # Grade 6-8
        "I was stressed about the project deadline, so I made a schedule to help me stay organized.",
        "I caught myself procrastinating, so I set a timer for 25 minutes and focused just on that.",
        "When I got a critique on my work, I took time to process it before responding.",
    ],
    "developing": [
        # Grade 2-3
        "I remembered to walk in the hallway.",
        "I raised my hand before speaking.",
        "I stayed in my seat during class.",
        # Grade 4-5
        "I tried to pay attention during the lesson.",
        "I waited for my turn during the game.",
        "I didn't talk when the teacher was talking.",
        # Grade 6-8
        "I turned in my homework on time.",
        "I tried to focus on my work.",
        "I followed the class rules.",
    ],
}

# Resilience responses
RESILIENCE_RESPONSES = {
    "high": [
        # Grade 2-3
        "I fell off the monkey bars and scraped my knee, but after the nurse put a bandage on it, I went back out and tried again. This time I made it across!",
        "My tower kept falling down, but I didn't give up. I tried building it different ways until I found one that worked.",
        "I got a spelling word wrong, but I practiced it five more times until I could spell it correctly every time.",
        # Grade 4-5
        "I failed the first math test of the year, which really discouraged me. But I met with the teacher, identified my weak areas, practiced every day, and improved my grade on every test after that.",
        "My science fair project didn't work as planned. Instead of quitting, I researched why it failed, adjusted my hypothesis, and redesigned the experiment. My revised project won an honorable mention!",
        "I didn't make the soccer team on my first try. I asked the coach for feedback, practiced the specific skills they mentioned all summer, and made the team the next year.",
        # Grade 6-8
        "I received harsh criticism on my first creative writing piece. Rather than giving up, I analyzed the feedback, studied writing techniques, joined a writing workshop, and submitted a revised piece that got published in the school magazine.",
        "My robotics team's design failed at the first competition. We didn't let that defeat us. We systematically analyzed what went wrong, redesigned our approach, tested extensively, and placed third at regionals.",
        "After being cut from the advanced math class, I felt devastated. But I used it as motivation to strengthen my foundation, worked with a tutor, and not only got into the advanced class the next year but became a peer tutor myself.",
    ],
    "medium": [
        # Grade 2-3
        "I couldn't tie my shoes at first, but I kept practicing until I got it.",
        "My picture didn't look how I wanted, so I tried again and it came out better.",
        "I missed the ball a few times, but I kept trying and finally hit it.",
        # Grade 4-5
        "I didn't win the art contest, but I was proud of my work and decided to enter again next year.",
        "My first presentation was really nervous, but each time I do one it gets a little easier.",
        "I struggled with long division at first, but I practiced and now I can do it without help.",
        # Grade 6-8
        "I didn't get the lead role in the play, but I worked hard in my supporting role and learned a lot.",
        "My first coding project had a lot of bugs, but I kept debugging until it finally worked.",
        "I was disappointed with my essay grade, but I used the feedback to improve my writing on the next assignment.",
    ],
    "developing": [
        # Grade 2-3
        "I tried again when I got it wrong.",
        "I didn't cry when I fell down.",
        "I finished my work even though it was hard.",
        # Grade 4-5
        "I kept working even though it was difficult.",
        "I didn't give up on the assignment.",
        "I tried to do better after making a mistake.",
        # Grade 6-8
        "I finished the project even though it was challenging.",
        "I didn't quit when it got hard.",
        "I tried to learn from my mistakes.",
    ],
}

# Mixed/general responses (show multiple skills)
MIXED_SKILL_RESPONSES = [
    # High-level responses (multiple skills evident)
    "In science class, our group's hypothesis was completely wrong. Instead of getting discouraged, we discussed what we learned from the failed experiment, revised our approach based on the data, and supported each other through the frustration. Our second attempt was successful!",
    "I noticed a new student struggling with the assignment and looking frustrated. I introduced myself, explained that I found it confusing at first too, then we worked through it together. By the end, we were both laughing about how we'd both initially misunderstood the directions.",
    "During our math tournament, I made a calculation error that cost our team points. I felt terrible, but my teammates reminded me that everyone makes mistakes. I apologized, took a deep breath, focused on the remaining problems, and we still placed in the top three.",
    # Medium-level responses
    "My friend and I had a disagreement about how to do our project. We were both getting upset, so we decided to take a break. When we came back, we listened to each other's ideas and found a way to combine them that was better than either of our original plans.",
    "I was having trouble with my reading assignment and was about to give up. Then I remembered what my teacher said about breaking big tasks into smaller ones. I read one page at a time and took short breaks. It took longer, but I finished it and understood the story.",
    # Grade-specific variations
    "[Grade 2-3] Today we built a tower with blocks and it kept falling down. Me and Jamie worked together and tried lots of different ways. We didn't get mad when it fell. Finally we figured out how to make it really tall and strong!",
    "[Grade 4-5] During gym class, I wasn't very good at the new game we were learning. Some kids were getting frustrated with me, but I asked them to be patient and kept trying. By the end of class, I was getting better, and I appreciated that they gave me a chance.",
    "[Grade 6-8] I procrastinated on my research paper and was panicking the night before it was due. I realized this was my own fault, so I stayed up late, did my best work given the time constraints, and learned a valuable lesson about time management. I've started all my assignments earlier since then.",
]

# Contextual variations (different settings)
CLASSROOM_CONTEXTS = [
    "During independent reading time, {}",
    "While working on our group project, {}",
    "In science lab today, {}",
    "During math class, {}",
    "When we were learning about {}, {}",
]

SOCIAL_CONTEXTS = [
    "At lunch today, {}",
    "During recess, {}",
    "On the bus, {}",
    "In the cafeteria, {}",
    "After school, {}",
]

EMOTIONAL_CONTEXTS = [
    "I felt {} when {}",
    "At first I was {}, but then {}",
    "{} made me feel {}, so I {}",
]

# Grade-level vocabulary and syntax patterns
GRADE_CHARACTERISTICS = {
    "2-3": {
        "avg_sentence_length": 8,
        "common_words": ["and", "then", "so", "because", "but", "really", "very"],
        "sentence_starters": ["I", "We", "My", "The", "When I"],
        "complexity": "simple",
    },
    "4-5": {
        "avg_sentence_length": 12,
        "common_words": [
            "because",
            "although",
            "instead",
            "during",
            "finally",
            "realized",
        ],
        "sentence_starters": ["During", "When", "After", "Although", "Instead of"],
        "complexity": "compound",
    },
    "6-8": {
        "avg_sentence_length": 15,
        "common_words": [
            "however",
            "consequently",
            "systematically",
            "analyzed",
            "concluded",
        ],
        "sentence_starters": [
            "Although",
            "Despite",
            "Consequently",
            "Having",
            "Through",
        ],
        "complexity": "complex",
    },
}


def get_responses_by_skill_and_level(skill_type: str, skill_level: str) -> list:
    """
    Get appropriate responses based on skill type and level.

    Args:
        skill_type: "empathy", "problem_solving", "self_regulation", "resilience"
        skill_level: "high", "medium", "developing"

    Returns:
        List of appropriate response strings
    """
    response_map = {
        "empathy": EMPATHY_RESPONSES,
        "problem_solving": PROBLEM_SOLVING_RESPONSES,
        "self_regulation": SELF_REGULATION_RESPONSES,
        "resilience": RESILIENCE_RESPONSES,
    }

    if skill_type not in response_map:
        return MIXED_SKILL_RESPONSES

    return response_map[skill_type].get(skill_level, [])


def get_grade_level_responses(grade: int) -> list:
    """Get responses appropriate for specific grade level."""
    if grade <= 3:
        grade_key = "2-3"
    elif grade <= 5:
        grade_key = "4-5"
    else:
        grade_key = "6-8"

    # Collect responses that match this grade range
    all_responses = []
    for skill_dict in [
        EMPATHY_RESPONSES,
        PROBLEM_SOLVING_RESPONSES,
        SELF_REGULATION_RESPONSES,
        RESILIENCE_RESPONSES,
    ]:
        for level in ["high", "medium", "developing"]:
            all_responses.extend(skill_dict[level])

    return all_responses
