// Questions and answers for readers new to Formula 1, machine learning or both.
// Numbers are the frozen results in the research report (paper/stint_theory_report.pdf);
// tested in test/faq.test.mjs so every link points to a real page.

export const GROUPS = [
  { id: "f1", label: "Formula 1 basics" },
  { id: "ml", label: "Machine learning basics" },
  { id: "found", label: "What the project found" },
  { id: "about", label: "About the project" },
];

export const FAQ = [
  // ------------------------------------------------------------------ Formula 1
  {
    id: "what-is-f1", group: "f1",
    q: "What happens in a Formula 1 race?",
    a: [
      "Twenty cars, two from each of ten teams, drive a fixed number of laps around a circuit, usually around 300 km in total. The first car to finish all the laps wins, and the top ten collect points for the championship.",
      "Because everyone drives the same distance, a race is really a contest of total time. Half a second lost on each of 50 laps adds up to 25 seconds, which is often the gap between winning and finishing off the podium.",
    ],
  },
  {
    id: "why-stop", group: "f1",
    q: "Why do drivers stop in the pit lane during a race?",
    a: [
      "To change tyres. Tyres lose grip as they are used, so a car on old tyres gets slower lap after lap. A pit stop swaps them for a fresh set, but driving through the pit lane and changing wheels costs time that the driver cannot win back on that lap.",
      "That is the whole strategy problem in one sentence: stop too often and you waste time in the pit lane, stop too rarely and you lose time on worn tyres.",
    ],
    fact: "In this data a pit stop costs about 25 seconds on average compared with staying on track.",
    links: [{ to: "/simulator", label: "Try timing a stop in the simulator" }],
  },
  {
    id: "compounds", group: "f1",
    q: "What are soft, medium and hard tyres?",
    a: [
      "Pirelli, the only tyre supplier, makes tyres from rubber of different softness. A soft tyre grips better and is faster when new, but wears out sooner. A hard tyre is slower but lasts longer. The medium sits in between.",
      "In a dry race every driver must use at least two different types, so every driver has to stop at least once. Choosing which tyres to use, in which order, is part of the strategy.",
    ],
    links: [{ to: "/tyres", label: "See how each tyre slows down in the tyre lab" }],
  },
  {
    id: "stint", group: "f1",
    q: "What is a stint?",
    a: [
      "A stint is the stretch of laps a driver completes on one set of tyres, from one pit stop to the next. A race with one stop has two stints, a race with two stops has three.",
      "The charts on this site draw each stint as a coloured bar: red for soft, yellow for medium and blue for hard.",
    ],
    links: [{ to: "/races", label: "Look at the stints of any race" }],
  },
  {
    id: "safety-car", group: "f1",
    q: "What is a safety car, and why does it change strategy?",
    a: [
      "After a crash or when debris is on the track, race officials can send out a safety car. All cars must follow it slowly in a line until the track is clear.",
      "Because everyone is going slowly, a pit stop during this time costs much less than usual. A well-timed safety car can turn a bad strategy into a good one, which is why strategy is a decision under uncertainty, not a fixed plan.",
    ],
    links: [{ to: "/simulator", label: "Add a safety car to a simulated race" }],
  },
  {
    id: "fuel", group: "f1",
    q: "Why do cars get faster during a race even though their tyres wear out?",
    a: [
      "Cars start with a full tank of fuel and burn it as they go, so they get lighter every lap. The track also gains grip as rubber is laid down on it. Both make every car faster as the race goes on.",
      "This hides the effect of tyre wear. If you just look at lap times, old tyres can even look faster, because the laps on old tyres are also the laps with less fuel. Separating the two was one of the main tasks of this project.",
    ],
    links: [{ to: "/tyres", label: "See the effect in the tyre lab" }],
  },

  // ------------------------------------------------------------------ machine learning
  {
    id: "what-is-model", group: "ml",
    q: "What does it mean to forecast a lap time?",
    a: [
      "It is like a weather forecast, but for the next lap. At the end of each lap, a model looks at what is known so far (how old the tyres are, how fast the driver has been, the weather) and guesses how long the next lap will take.",
      "When the lap is driven, the guess can be checked. Doing this tens of thousands of times shows how good each method really is.",
    ],
    links: [{ to: "/next-lap", label: "See how close the guesses were" }],
  },
  {
    id: "ml-vs-dl", group: "ml",
    q: "What is the difference between statistics, machine learning and deep learning?",
    a: [
      "All three learn patterns from past data to make guesses about new cases. They differ in how flexible they are.",
      "A statistical model is a simple formula, for example: next lap = last lap plus a small amount for each lap of tyre age. Machine learning lets the computer find more complicated rules on its own. Deep learning uses neural networks, very flexible models with many adjustable parts, loosely inspired by the brain. They power image recognition and chatbots.",
      "More flexible is not always better. A flexible model can learn noise as if it were a pattern, and it needs more data and computing power. Whether the extra flexibility pays off is exactly what this project tested.",
    ],
  },
  {
    id: "trees", group: "ml",
    q: "What are random forests and gradient-boosted trees (XGBoost)?",
    a: [
      "A decision tree is a chain of yes-or-no questions: are the tyres older than 15 laps? Is it raining? Each path ends in a guess.",
      "One tree is crude, so these methods combine many. A random forest averages hundreds of trees, each trained on a slightly different sample. Gradient boosting builds trees one after another, each one trying to fix the mistakes of the trees before it. XGBoost is the most widely used version of gradient boosting.",
    ],
    links: [{ to: "/models", label: "Compare all ten models" }],
  },
  {
    id: "networks", group: "ml",
    q: "What are the MLP, LSTM and TCN?",
    a: [
      "They are the three neural networks tested here. The MLP (multilayer perceptron) is the basic kind: it takes the same list of facts the tree models see and passes them through layers of simple calculations.",
      "The LSTM (long short-term memory) and the TCN (temporal convolutional network) also read the driver's last ten laps in order, the way you read a sentence word by word. The idea is that the order of recent laps might hold information a summary misses.",
      "Comparing the MLP with XGBoost tests the learner on the same inputs. Comparing the LSTM and TCN with the MLP tests whether reading laps in order adds anything.",
    ],
  },
  {
    id: "persistence", group: "ml",
    q: "Why compare every model with just repeating the last lap?",
    a: [
      "The simplest possible guess is that the next lap will be as fast as the last clean one. Forecasters call this persistence. It costs nothing and is surprisingly hard to beat.",
      "If a complex model cannot beat it, the model is not useful. So every result on this site is reported as how much of the persistence guess's error a model removes.",
    ],
    fact: "The best models removed about 12% of the persistence guess's error on the next lap, and 23% over ten laps.",
  },
  {
    id: "mae", group: "ml",
    q: "What does an error of 0.33 seconds mean?",
    a: [
      "It is the average size of a miss. If a model guessed 1:32.0 and the lap took 1:32.4, the miss was 0.4 seconds. Average that over every lap and you get the mean absolute error, the main score on this site. Lower is better.",
      "For scale, 0.33 seconds is about the time it takes to blink, on a lap that lasts around a minute and a half.",
    ],
    fact: "Best next-lap error: 0.333 s. Repeating the last lap: 0.382 s.",
  },
  {
    id: "test-set", group: "ml",
    q: "What is a locked test set, and why does it matter?",
    a: [
      "Think of an exam. If a student sees the questions in advance, a high score proves nothing. The same is true for models: if you keep adjusting a model until it does well on some races, its score on those races is no longer a fair test.",
      "So the last twelve races of 2025 were locked away in the code before any model was built. All the tuning happened on earlier races. The locked races were opened once, at the end, and every opening was logged.",
    ],
    links: [{ to: "/methods", label: "Read how the test was set up" }],
  },
  {
    id: "preregistration", group: "ml",
    q: "What is pre-registration?",
    a: [
      "It means writing down, before seeing the results, exactly which comparisons you will make and what will count as a win. It is like agreeing on the marking scheme before the exam is marked.",
      "Without it, a researcher could try many comparisons and report only the ones that look good. The plans for this project were saved in the public repository, with a timestamp, before the test races were opened.",
    ],
    links: [{ to: "/reliability", label: "See the reliability checks" }],
  },
  {
    id: "equivalent", group: "ml",
    q: "What does it mean when two models are called equivalent?",
    a: [
      "Not finding a difference is not the same as showing there is none. So before the test, a margin was fixed: if two models differ by less than one hundredth of a second per lap, the difference is too small to matter.",
      "Two models are called equivalent only when the data show, with 90% confidence, that their gap is inside that margin. It is a positive finding, not just a failure to find a winner.",
    ],
    links: [{ to: "/next-lap", label: "See the five pre-registered comparisons" }],
  },
  {
    id: "ranges", group: "ml",
    q: "Why do results come with ranges instead of one number?",
    a: [
      "Every result is measured on a limited number of races, so it would come out a little differently on other races. A range, such as 0.29 to 0.38 seconds, shows how much the result could plausibly move.",
      "When two ranges overlap a lot, the data cannot tell the two results apart. Short ranges mean a precise result, wide ranges mean be careful.",
    ],
  },

  // ------------------------------------------------------------------ findings
  {
    id: "did-dl-win", group: "found",
    q: "So, did deep learning win?",
    a: [
      "No. On the next lap, the three neural networks and gradient-boosted trees were equivalent: they differed by less than half a hundredth of a second per lap. Over ten laps, the boosted trees were slightly more accurate than the LSTM.",
      "The neural networks also took far longer to train. More complexity bought no extra accuracy here, which suggests the limit is the information in public timing data, not the model.",
    ],
    fact: "Training time: TCN 6,480 s, averaged XGBoost 76 s, about 85 times as much for the same accuracy.",
    links: [{ to: "/models", label: "Open the model arena" }],
  },
  {
    id: "tyre-cost", group: "found",
    q: "How much time does an old tyre actually cost?",
    a: [
      "Once the effect of burning fuel is removed, each extra lap on a set of tyres is linked to a loss of about 0.04 to 0.07 seconds per lap, depending on the tyre. Soft tyres lose pace fastest, hard tyres slowest.",
      "That sounds tiny, but it adds up. Over a 25-lap stint on medium tyres, the losses add up to about 14 seconds, more than half the cost of a pit stop. This is why the choice between one and two stops is often close.",
    ],
    fact: "Per extra lap of tyre age: soft 0.068 s, medium 0.048 s, hard 0.042 s.",
    links: [{ to: "/tyres", label: "Explore the tyre lab" }],
  },
  {
    id: "economics", group: "found",
    q: "Why would an economist find this interesting?",
    a: [
      "A pit stop is a classic replacement decision. A tyre is like a machine that loses value with use, and the team decides when to pay a fixed cost to replace it, the same question a firm asks about an ageing truck or engine.",
      "The model comparison is also a question of returns on investment: the neural networks cost many times more computing for no gain in accuracy, a marginal return close to zero.",
    ],
  },
  {
    id: "simulator-accuracy", group: "found",
    q: "How accurate is the strategy simulator?",
    a: [
      "It was checked on real races it had never seen. It predicts pace on new tyres after a stop much better than a simple guess, but over the rest of a race it is on average about 19 seconds too slow.",
      "Its ranges are also too narrow: a range that should contain the real result 90% of the time contained it 74% of the time. Comparisons between two plans are more reliable than absolute times, because most of the error is shared by both plans.",
    ],
    fact: "Pace after a stop: error 0.88 s per lap against 1.60 s for the simple guess.",
    links: [{ to: "/reliability", label: "See every reliability check" }],
  },
  {
    id: "who-wins", group: "found",
    q: "Can the simulator tell me who would have won?",
    a: [
      "No. It simulates one car against the clock. It does not model overtaking, traffic, other cars' strategies or finishing positions. It answers a narrower question: for this driver, which plan of stops gives the shortest race time, and how sure can we be?",
    ],
  },
  {
    id: "monza", group: "found",
    q: "What happened at Monza in 2024?",
    a: [
      "Ferrari kept Charles Leclerc on one stop while McLaren stopped Oscar Piastri twice. Leclerc won by 2.664 seconds, holding on with much older tyres.",
      "The simulator, which never saw this race, agrees that one stop was faster, but it puts the advantage of one stop at about 11 to 14 seconds, far more than the real gap. A likely reason, not tested here, is that the newly resurfaced track wore tyres faster than earlier years at Monza suggested.",
    ],
    links: [{ to: "/case-study", label: "Read the case study" }],
  },

  // ------------------------------------------------------------------ about
  {
    id: "data-source", group: "about",
    q: "Where does the data come from? Is it official?",
    a: [
      "From OpenF1, a free, community-run service that republishes Formula 1 timing data. It is not run by Formula 1. The project uses 69 races from 2023 to 2025, about 77,000 laps in total.",
      "Because the timing data belongs to Formula 1, this site shows only results built from it, not the raw lap-by-lap tables.",
    ],
    links: [{ to: "/data", label: "See what the data covers" }],
  },
  {
    id: "where-start", group: "about",
    q: "I am new to all of this. Where should I start?",
    a: [
      "Start with the case study: it tells the story of one real decision. Then open the simulator, pick a race and a driver, and compare two plans yourself. The tyre lab shows how much each type of tyre slows down with age.",
      "If you want the full detail, the research report explains every method and result.",
    ],
    links: [
      { to: "/case-study", label: "Case study" },
      { to: "/simulator", label: "Simulator" },
      { to: "/tyres", label: "Tyre lab" },
    ],
    report: true,
  },
  {
    id: "who", group: "about",
    q: "Who made this, and can I check the work?",
    a: [
      "STINT THEORY is an independent research project by Nahian Ibnat. It is not affiliated with Formula 1, the FIA, Pirelli or any team.",
      "All the code, the pre-registrations and a log of every change to the models are public, so anyone can rerun the analysis.",
    ],
    links: [{ to: "/limits", label: "Limits and how to rerun everything" }],
    report: true,
  },
];
