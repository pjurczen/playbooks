# Simplified Technical English

ASD-STE100 Issue 9 (2025) is the standard. It has 53 writing rules in nine sections and a dictionary of about 900 approved words. The dictionary is not in this
repository, because the standard is copyrighted. When the repo has the specification, `.claude/designs.md` names its location. Then read Part 1 in full and
check each word against Part 2. Without the specification, apply the rules below and use the simplest common word, one word for one thing.

A design is descriptive text. Apply sections 1 to 4, 6, 8 and 9 to it. A skill, a prompt and an instruction to the user are procedural text. Apply sections 1 to
5, 8 and 9 to them. A warning gets section 7.

## Section 1: Words

- 1.1 Use only approved words, technical nouns and technical verbs. A technical noun is the name of a thing of the project: a glossary term, a class, a file, a
  message. A technical verb is an action of the project: to deploy, to commit.
- 1.2 Use an approved word only as its approved part of speech.
- 1.3 Use an approved word only with its approved meaning.
- 1.4 Use only the approved forms of verbs and adjectives.
- 1.5 You can use a word that fits a technical noun category.
- 1.6 Use an unapproved word only when it is a technical noun or part of one.
- 1.7 Do not use a technical noun as a verb.
- 1.8 Use the technical nouns of your company, industry or subject. In a repo, these are the glossary terms.
- 1.9 When you must select a technical noun, select one that is short and easy to understand.
- 1.10 Do not use a regional word, slang or jargon as a technical noun.
- 1.11 Do not use different technical nouns for the same item. Do not translate a technical noun.
- 1.12 You can use a verb that fits a technical verb category.
- 1.13 Do not use a technical verb as a noun.
- 1.14 Use American spelling unless an official directive says otherwise.

## Section 2: Multi-word nouns

- 2.1 Write a multi-word noun of not more than three words.
- 2.2 When a technical noun has more than three words, write it in full the first time. Then give it a short form and use the short form.

## Section 3: Verbs

- 3.1 Use only the verb forms that the dictionary gives.
- 3.2 Use only these forms: the infinitive, the imperative, the simple present, the simple past, the simple future, the past participle as an adjective.
- 3.3 Use the past participle only as an adjective: an approved design, a resolved identity.
- 3.4 Do not use an auxiliary verb to make a complex verb form. Write "the test fails", not "the test would have failed".
- 3.5 Use the "-ing" form of a verb only in a technical noun: brainstorming, the writing-plans skill.
- 3.6 Use the active voice. In descriptive text, use the passive voice only when the agent is unknown.
- 3.7 Use a verb for an action, not a noun. Write "the service decides", not "the service makes a decision".

## Section 4: Sentences

- 4.1 Write short and clear sentences. In descriptive text, give each sentence one topic. Say how the thing works. An abstract sentence stands only as a topic
  sentence, with the concrete facts under it (6.5).
- 4.2 Do not omit a word to make a sentence shorter. Keep the subject, the verb and the articles. Do not use a contraction.
- 4.3 Use a vertical list for complex text. End the sentence before the list with a colon. Start each item with an uppercase letter. Put a period after an item
  that is a full sentence and after the last item. Do not put a comma or a semicolon after an item.
- 4.4 Use a connecting word or phrase to connect sentences with related topics: and, but, then, thus, as a result.
- 4.5 Put an article or a demonstrative adjective before a noun: the design, this rule.

## Section 5: Procedural writing

- 5.1 Write not more than 20 words in a sentence.
- 5.2 Write one instruction in each sentence, unless two actions occur at the same time.
- 5.3 Write an instruction in the imperative: "Ask one question."
- 5.4 When the reader must know a condition first, start with the condition. Divide it from the command with a comma: "If the user brings a design, apply the
  ADR test first."
- 5.5 Write a note to give information, not an instruction.

## Section 6: Descriptive writing

- 6.1 Give information gradually. Give each sentence one subject.
- 6.2 Use the same key words and key phrases through the text to connect its ideas. Do not change a term once you use it.
- 6.3 Write not more than 25 words in a sentence.
- 6.4 Use a paragraph to keep related information together.
- 6.5 Give each paragraph one topic. Start the paragraph with the sentence that states the topic. A topic sentence can name a cause or a dependency. The
  sentences after it give the facts.
- 6.6 Write not more than six sentences in a paragraph.
- The imperative is not permitted in descriptive text.

## Section 7: Safety instructions

- 7.1 Use a word that identifies the level of risk: warning, caution.
- 7.2 Start a safety instruction with a clear command or condition.
- 7.3 Give an explanation that shows the risk or the possible result.

## Section 8: Punctuation and word count

- 8.1 Use all standard punctuation marks but not the semicolon.
- 8.2 Use a hyphen to connect words that are directly related.
- 8.3 Use parentheses for a reference, an identifier, a work-step mark or an abbreviation.
- 8.4 In a vertical list, a colon ends a sentence for the word count.
- 8.5 Text in parentheses counts as one word.
- 8.6 A number, a number with a unit, an abbreviation, an identifier, quoted text, a title and a proper noun each count as one word.
- 8.7 A hyphenated word counts as one word.

## Section 9: Writing practices

- 9.1 When a word-for-word replacement is not sufficient, change the construction of the sentence.
- 9.2 Use each approved word correctly.
- 9.3 Do not make a phrasal verb from two words. Write "remove", not "take off".
- 9.4 Use a consistent style for terminology and wording.

## Check your text

- Count the words of each sentence: 20 in an instruction, 25 in a description.
- Count the sentences of each paragraph: six.
- Find each "-ing" word that is not a technical noun. Find each semicolon. Find each passive sentence. Find each contraction. Change them.
- Find each term that has a second name in the text. Keep one name.
