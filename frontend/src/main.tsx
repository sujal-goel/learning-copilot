import { FormEvent, ReactNode, useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'
import { mockProfile } from './data/mockProfile'
import { mockCourses } from './data/mockCourses'
import { mockProgress } from './data/mockProgress'


type Page = 'landing' | 'login' | 'setup' | 'profile' | 'roadmap' | 'courses' | 'course' | 'dashboard' | 'mentor'
type Learner = { name: string; email: string; goal: string; level: string; hours: string; timeline: string; interests: string, currentSkills: string[] }
type Account = { email: string; password: string; learner: Learner }
const demo: Learner = { name: 'Alex Morgan', email: '', goal: 'AI Engineer', level: 'Intermediate', hours: '2 hours', timeline: '6 months', interests: '', currentSkills: [] }
const readAccounts = (): Account[] => { try { return JSON.parse(localStorage.getItem('pathpilot-accounts') || '[]') } catch { return [] } }
const getLearner = (): Learner => { try { return { ...demo, ...JSON.parse(localStorage.getItem('pathpilot-learner') || '{}') } } catch { return demo } }
const initials = (name: string) => name.split(' ').map(x => x[0]).join('').slice(0, 2).toUpperCase()
const Button = ({ children, onClick, kind = 'primary', type = 'button' }: { children: ReactNode; onClick?: () => void; kind?: 'primary' | 'ghost' | 'outline'; type?: 'button' | 'submit' }) => <button type={type} className={`btn ${kind}`} onClick={onClick}>{children}</button>
const Logo = () => <button className="logo" onClick={() => location.hash = 'landing'}><span>✦</span> PathPilot <i>AI</i></button>
const GoogleButton = ({ onClick }: { onClick: () => void }) => <button type="button" className="google-login" onClick={onClick}><b>G</b> Continue with Google</button>
function Navbar({ go }: { go: (p: Page) => void }) { return <header className="navbar"><Logo /><nav><button onClick={() => go('roadmap')}>Roadmap</button><button onClick={() => go('courses')}>Courses</button><button onClick={() => go('mentor')}>AI Mentor</button></nav><div className="nav-actions"><Button kind="ghost" onClick={() => go('login')}>Log in</Button><Button onClick={() => go('setup')}>Get started →</Button></div></header> }
function Shell({ page, go, children }: { page: Page; go: (p: Page) => void; children: ReactNode }) { const p = getLearner(); const [open, setOpen] = useState(false); const links: [Page, string][] = [['dashboard', '⌂ Dashboard'], ['profile', '◉ My Profile'], ['roadmap', '◇ Roadmap'], ['courses', '▣ Courses'], ['mentor', '✦ AI Mentor']]; const navigate = (id: Page) => { setOpen(false); go(id) }; return <div className="app-shell"><aside className={`sidebar ${open ? 'open' : ''}`}><Logo /><div className="side-links">{links.map(([id, title]) => <button className={page === id ? 'active' : ''} onClick={() => navigate(id)} key={id}>{title}</button>)}</div><div className="sidebar-bottom"><div className="mini-avatar">{initials(p.name)}</div><div><strong>{p.name}</strong><small>{p.level} learner</small></div></div></aside>{open && <button aria-label="Close navigation" className="backdrop" onClick={() => setOpen(false)} />}<main className="app-content"><div className="app-top"><button className="menu-in-app" onClick={() => setOpen(true)}>☰</button><div /><button className="bell">♧</button><div className="avatar">{initials(p.name)}</div></div>{children}</main></div> }
function Heading({ eyebrow, title, children }: { eyebrow: string; title: ReactNode; children?: ReactNode }) { return <section className="page-heading"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1>{children}</div></section> }
function Landing({ go }: { go: (p: Page) => void }) { const features = [['✧', 'AI Skill Gap Analysis'], ['◇', 'Personalized Roadmaps'], ['▣', 'Course Recommendations'], ['✦', 'AI Mentor'], ['◔', 'Progress Tracking']]; return <div className="landing"><Navbar go={go} /><section className="hero"><div className="hero-copy"><div className="eyebrow">✦ YOUR PERSONAL AI LEARNING COMPANION</div><h1>Find your path.<br /><em>Build your future.</em></h1><p>PathPilot AI turns your career goals into a personalized learning journey — with the clarity and support to get you there.</p><div className="hero-actions"><Button onClick={() => go('setup')}>Start your journey →</Button><Button kind="ghost" onClick={() => go('login')}>Log in</Button></div></div><div className="hero-visual"><div className="orb orb-one" /><div className="orb orb-two" /><div className="journey-card"><div><span className="journey-label">YOUR LEARNING JOURNEY</span><b>Personalized path</b><small>Built around your goal</small></div><div className="journey-progress"><div><i /></div><small>Ready when you are</small></div></div><div className="float-card card-skill"><span>✦</span><div><small>NEXT UP</small><b>Deep Learning</b></div></div></div></section><section className="features"><div className="section-intro"><div className="eyebrow">HOW PATHPILOT WORKS</div><h2>Everything you need to<br /><em>keep moving forward.</em></h2></div><div className="feature-grid">{features.map(([icon, title]) => <article className="feature-card" key={title}><span>{icon}</span><h3>{title}</h3><p>Personalized support designed around your learning journey.</p></article>)}</div></section></div> }

function Login({ go, refresh }: { go: (p: Page) => void; refresh: () => void }) { const [error, setError] = useState(''); const submit = (e: FormEvent<HTMLFormElement>) => { e.preventDefault(); const form = new FormData(e.currentTarget); const email = String(form.get('email')).toLowerCase().trim(); const password = String(form.get('password')); const account = readAccounts().find(x => x.email === email && x.password === password); if (!account) { setError('Email or password is incorrect. Create a profile if you are new.'); return } localStorage.setItem('pathpilot-learner', JSON.stringify(account.learner)); localStorage.setItem('pathpilot-current-email', email); refresh(); go('dashboard') }; return <div className="auth-page"><Logo /><form className="auth-card" onSubmit={submit}><div className="auth-symbol">✦</div><div className="eyebrow">WELCOME BACK</div><h1>Log in to your path.</h1><p>Use your saved credentials, or continue with Google.</p><GoogleButton onClick={() => setError('Google sign-in UI is ready. Connect Google OAuth credentials to enable it.')} /><div className="auth-divider"><span>or continue with email</span></div><label>Email<input required name="email" type="email" placeholder="you@example.com" /></label><label>Password<input required name="password" type="password" placeholder="Your password" /></label>{error && <div className="auth-error">{error}</div>}<Button type="submit">Log in →</Button><button type="button" className="auth-switch" onClick={() => go('setup')}>New to PathPilot? Create an account</button></form></div> }

function Setup({ go, refresh }: { go: (p: Page) => void; refresh: () => void }) {
  const [level, setLevel] = useState('Intermediate');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const f = new FormData(e.currentTarget);
    const email = String(f.get('email')).toLowerCase().trim();

    if (readAccounts().some(x => x.email === email)) {
      setError('An account with this email already exists. Please log in instead.');
      return;
    }

    const currentSkills = String(
      f.get('skills') || ''
    )
      .split(',')
      .map(s => s.trim())
      .filter(Boolean);

    const profile: Learner = {
      name: String(f.get('name')).trim(),
      email,
      goal: String(f.get('goal')),
      level,
      hours: String(f.get('hours')),
      timeline: String(f.get('timeline')),
      interests: String(f.get('interests')),
      currentSkills
    };

    try {
      const response = await fetch(
        'http://localhost:8000/ai/generate',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            goal: profile.goal,
            level: profile.level,
            hours: profile.hours,
            timeline: profile.timeline,
            interests: profile.interests,
            currentSkills: currentSkills
          })
        }
      );

      const roadmapData = await response.json();

      console.log('Roadmap:', roadmapData);

      localStorage.setItem(
        'pathpilot-roadmap',
        JSON.stringify(roadmapData)
      );

    } catch (err) {
      console.error(err);
      setError('Failed to generate roadmap');
      return;
    }

    const account: Account = {
      email,
      password: String(f.get('password')),
      learner: profile
    };

    localStorage.setItem(
      'pathpilot-accounts',
      JSON.stringify([...readAccounts(), account])
    );

    localStorage.setItem(
      'pathpilot-learner',
      JSON.stringify(profile)
    );

    localStorage.setItem(
      'pathpilot-current-email',
      email
    );

    refresh();

    setLoading(true);

    setTimeout(() => {
      go('profile');
    }, 600);
  };

  if (loading) {
    return (
      <div className="auth-page">
        <Logo />
        <div className="loading">
          <span className="spinner" />
          Creating your account...
        </div>
      </div>
    );
  }

  return (
    <div className="setup-page">
      <Navbar go={go} />

      <main className="setup-main">
        <div className="setup-heading">
          <div className="eyebrow">CREATE YOUR ACCOUNT</div>
          <h1>
            Tell us where
            <br />
            you want to <em>go.</em>
          </h1>
          <p>Your login and profile will be saved on this browser.</p>
        </div>

        <form className="goal-form" onSubmit={submit}>
          <GoogleButton
            onClick={() =>
              setError(
                'Google sign-up UI is ready. Connect Google OAuth credentials to enable it.'
              )
            }
          />

          <div className="auth-divider">
            <span>or sign up with email</span>
          </div>

          <label>
            Your name
            <input
              required
              name="name"
              placeholder="e.g. Priya Sharma"
            />
          </label>

          <div className="form-split">
            <label>
              Email
              <input
                required
                name="email"
                type="email"
                placeholder="you@example.com"
              />
            </label>

            <label>
              Password
              <input
                required
                name="password"
                type="password"
                minLength={4}
                placeholder="At least 4 characters"
              />
            </label>
          </div>

          <label>
            Career goal
            <select required name="goal" defaultValue="">
              <option value="" disabled>
                Choose your destination
              </option>
              <option>AI Engineer</option>
              <option>Data Scientist</option>
              <option>Product Manager</option>
            </select>
          </label>

          <label>
            Experience level
            <div className="choice-row">
              {['Beginner', 'Intermediate', 'Advanced'].map(x => (
                <button
                  key={x}
                  type="button"
                  className={x === level ? 'selected' : ''}
                  onClick={() => setLevel(x)}
                >
                  {x}
                </button>
              ))}
            </div>
          </label>

          <div className="form-split">
            <label>
              Study hours per day
              <select required name="hours" defaultValue="">
                <option value="" disabled>
                  Select hours
                </option>
                <option>1 hour</option>
                <option>2 hours</option>
                <option>3+ hours</option>
              </select>
            </label>

            <label>
              Target timeline
              <select required name="timeline" defaultValue="">
                <option value="" disabled>
                  Select timeline
                </option>
                <option>3 months</option>
                <option>6 months</option>
                <option>12 months</option>
              </select>
            </label>
          </div>

          <label>
            Interests
            <input
              name="interests"
              placeholder="e.g. Generative AI, computer vision..."
            />
          </label>

          <label>
            Current Skills
            <input
              name="skills"
              placeholder="e.g. Python, SQL, Excel"
            />
          </label>

          {error && (
            <div className="auth-error">
              {error}
            </div>
          )}

          <Button type="submit">
            Create account & learning path →
          </Button>

          <button
            type="button"
            className="auth-switch"
            onClick={() => go('login')}
          >
            Already registered? Log in
          </button>
        </form>
      </main>
    </div>
  );
}

function Skill({ title, kind }: { title: string; kind: string }) { return <div className={`skill-card ${kind}`}><span>{kind === 'current' ? '✓' : '◎'}</span><div><strong>{title}</strong><small>{kind === 'current' ? 'In your toolkit' : 'Recommended next'}</small></div></div> }

function Profile({ page, go }: { page: Page; go: (p: Page) => void }) {

  const p = getLearner();

  const roadmapData = JSON.parse(
    localStorage.getItem("pathpilot-roadmap") || "{}"
  );

  const currentSkills =
    roadmapData?.skill_gap?.current_skills || [];

  const missingSkills =
    roadmapData?.skill_gap?.missing_skills || [];

  return (
    <Shell page={page} go={go}>
      <Heading
        eyebrow="YOUR LEARNER PROFILE"
        title={
          <>
            Great to meet you, <em>{p.name.split(" ")[0]}.</em>
          </>
        }
      >
        <p>
          Here’s the starting point for your personalized {p.goal} path.
        </p>
      </Heading>

      <section className="profile-hero">
        <div className="profile-person">
          <div className="profile-avatar">
            {initials(p.name)}
          </div>

          <div>
            <span>CAREER DESTINATION</span>
            <h2>{p.goal}</h2>
            <p>
              Your personalized {p.timeline} learning path is ready.
            </p>
          </div>
        </div>

        <div className="level-pill">
          <span>◇</span>

          <div>
            <small>YOUR LEVEL</small>
            <strong>{p.level}</strong>
          </div>
        </div>
      </section>

      <section className="profile-skills">

        <div>
          <div className="section-label">
            <h2>Current skills</h2>
            <p>Your existing foundation.</p>
          </div>

          <div className="skill-list">
            {currentSkills.length > 0 ? (
              currentSkills.map((x: string) => (
                <Skill
                  title={x}
                  kind="current"
                  key={x}
                />
              ))
            ) : (
              <p>No skills detected yet.</p>
            )}
          </div>
        </div>

        <div>
          <div className="section-label">
            <h2>Skills to build</h2>
            <p>
              Focus areas that unlock your goal.
            </p>
          </div>

          <div className="skill-list">
            {missingSkills.map((x: string) => (
              <Skill
                title={x}
                kind="missing"
                key={x}
              />
            ))}
          </div>
        </div>

      </section>
    </Shell>
  );
}

function Roadmap({
  page,
  go,
}: {
  page: Page;
  go: (p: Page) => void;
}) {
  const roadmapData = JSON.parse(
    localStorage.getItem("pathpilot-roadmap") || "{}"
  );

  const roadmap = roadmapData?.roadmap || {};

  const roadmapCards = Object.entries(roadmap).map(
    ([month, topics]: any, index) => ({
      month: month.replace("_", " ").toUpperCase(),
      title: `Learning Plan ${index + 1}`,
      items: Array.isArray(topics) ? topics : [],
      tone: ["blue", "violet", "pink", "orange", "green", "blue"][
        index % 6
      ],
    })
  );

  return (
    <Shell page={page} go={go}>
      <Heading
        eyebrow="YOUR PERSONALIZED PATH"
        title={
          <>
            From here to <em>your goal.</em>
          </>
        }
      >
        <p>
          A personalized roadmap generated specifically for your career goal.
        </p>
      </Heading>

      <div className="roadmap-grid">
        {roadmapCards.length > 0 ? (
          roadmapCards.map((x) => (
            <article
              className={`roadmap-card ${x.tone}`}
              key={x.month}
            >
              <span className="month">{x.month}</span>

              <div className="roadmap-icon">✧</div>

              <h3>{x.title}</h3>

              <ul>
                {x.items.map((item: string) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>

              <button onClick={() => go("courses")}>
                Explore module →
              </button>
            </article>
          ))
        ) : (
          <div>
            <h3>No roadmap found</h3>
            <p>Create an account first to generate a roadmap.</p>
          </div>
        )}
      </div>
    </Shell>
  );
}

function Courses({ page, go }: { page: Page; go: (p: Page) => void }) {

  const [courses, setCourses] = useState<any[]>([]);

  const roadmapData = JSON.parse(
    localStorage.getItem("pathpilot-roadmap") || "{}"
  );

  const roadmap = roadmapData?.roadmap || {};

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/courses/python"
      );

      const data = await response.json();

      setCourses(data);
    } catch (err) {
      console.error(err);
    }
  };

  const monthTitles = [
    "Python Foundations",
    "Data Analysis",
    "Statistics",
    "Machine Learning",
    "Advanced ML",
    "Capstone Project"
  ];

  const generatedCourses = Object.entries(roadmap).map(
    ([month, topics]: any, index) => ({
      title: monthTitles[index] || `Month ${index + 1}`,
      difficulty:
        roadmapData?.profile?.experience_level || "Beginner",
      platform: "AI Generated",
      description: Array.isArray(topics)
        ? topics.join(" • ")
        : "",
      reason: `Based on your ${month.replace("_", " ")} learning goals.`,
      color: ["blue", "violet", "pink", "orange", "green", "blue"][
        index % 6
      ]
    })
  );

  const coursesToShow =
    courses.length > 0
      ? courses
      : generatedCourses;

  return (
    <Shell page={page} go={go}>
      <Heading
        eyebrow="RECOMMENDED FOR YOU"
        title={
          <>
            Learn what moves you <em>forward.</em>
          </>
        }
      >
        <p>
          Picked to close the gaps between where you are
          and where you're headed.
        </p>
      </Heading>

      <div className="course-grid">
        {coursesToShow.map((c: any, index: number) => (
          <article className="course-card" key={c.title}>

            <div
              className={`course-cover ${
                ["blue", "violet", "pink", "orange", "green"][
                  index % 5
                ]
              }`}
            >
              <span>✦</span>
              <small>{c.platform}</small>
            </div>

            <div className="course-body">

              <div className="course-meta">
                <span>{c.difficulty}</span>
                <span>{c.platform}</span>
              </div>

              <h3>{c.title}</h3>

              <p>{c.description?.length>180
                ? c.description.substring(0,180) + "..."
              : c.description}
              </p>

              <div className="reason">
                <b>Recommended Course</b>
                <br />
                Learn skills relevant to your roadmap.
              </div>

              <Button
                kind="outline"
                onClick={() => {
                  if (c.url) {
                    window.open(c.url, "_blank");
                  } else {
                    alert("Course link not available yet");
                  }
                }}
              >
                View course →
              </Button>

            </div>
          </article>
        ))}
      </div>
    </Shell>
  );
}

function CoursePage({
  page,
  go,
}: {
  page: Page;
  go: (p: Page) => void;
}) {
  return (
    <Shell page={page} go={go}>
      <Heading
        eyebrow="COURSE DETAILS"
        title={<>Python Foundations</>}
      >
        <p>Learn Python fundamentals for Data Science.</p>
      </Heading>

      <div className="course-details">
        <h2>Topics Covered</h2>

        <ul>
          <li>Python Syntax</li>
          <li>Lists & Dictionaries</li>
          <li>Functions</li>
          <li>File Handling</li>
        </ul>

        <Button
          kind="outline"
          onClick={() => go("courses")}
        >
          Back to Courses
        </Button>
      </div>
    </Shell>
  );
}

function Stat({ icon, label, value, note, color }: { icon: string; label: string; value: string; note: string; color: string }) { return <article className={`stat-card ${color}`}><div className="stat-icon">{icon}</div><small>{label}</small><strong>{value}</strong><p>{note}</p></article> }

function Dashboard({ page, go }: { page: Page; go: (p: Page) => void }) { const p = getLearner(); 
  const roadmapData = JSON.parse(
  localStorage.getItem("pathpilot-roadmap") || "{}"
    );

  const missingSkills =
    roadmapData?.skill_gap?.missing_skills?.length || 0;

  const roadmapMonths =
    Object.keys(roadmapData?.roadmap || {}).length;

  const experienceLevel =
    roadmapData?.profile?.experience_level || p.level;

  const [focus, setFocus] = useState('roadmap'); const logout = () => { localStorage.removeItem('pathpilot-learner'); localStorage.removeItem('pathpilot-current-email'); go('login') }; const focusCopy = focus === 'roadmap' ? 'Follow the modules built around your career goal.' : focus === 'profile' ? 'Review your skills and tune your learning preferences.' : 'Ask your mentor for a focused study plan.'; return <Shell page={page} go={go}><section className="dashboard-greeting"><div><div className="eyebrow">YOUR LEARNING DASHBOARD</div><h1>Good morning, <em>{p.name.split(' ')[0]}.</em></h1><p>Goal: {p.goal} · Level: {experienceLevel}</p></div><div className="dashboard-actions"><Button kind="outline" onClick={logout}>Log out</Button><Button onClick={() => go('mentor')}>Ask AI Mentor ✦</Button></div></section><section className="dashboard-grid"><article className="overall-card journey-action"><div><small>YOUR PERSONAL PLAN</small><h2>{p.goal}</h2><p>{p.timeline} target · {p.hours} study routine</p></div><div className="plan-actions"><Button onClick={() => go('roadmap')}>View roadmap →</Button><Button kind="outline" onClick={() => go('profile')}>Edit profile</Button></div><footer><span>Built for {p.name}</span></footer></article><Stat icon="◷" label="STUDY ROUTINE" value={p.hours} note="Set during profile creation" color="orange" /><Stat icon="◎" label="TARGET TIMELINE" value={p.timeline} note="You can update this anytime" color="green" />
  <Stat
  icon="★"
  label="MISSING SKILLS"
  value={String(missingSkills)}
  note="Detected by AI roadmap"
  color="blue"
  />

  <Stat
  icon="✦"
  label="ROADMAP MODULES"
  value={String(roadmapMonths)}
  note="Generated learning path"
  color="pink"
  />

  <article className="skill-progress learning-focus"><small>CHOOSE YOUR NEXT STEP</small><h2>What would help today?</h2><div className="focus-buttons"><button className={focus === 'roadmap' ? 'selected' : ''} onClick={() => setFocus('roadmap')}>Explore roadmap</button><button className={focus === 'profile' ? 'selected' : ''} onClick={() => setFocus('profile')}>Review profile</button><button className={focus === 'mentor' ? 'selected' : ''} onClick={() => setFocus('mentor')}>Ask mentor</button></div><p className="focus-copy">{focusCopy}</p><Button kind="outline" onClick={() => go(focus === 'mentor' ? 'mentor' : focus === 'profile' ? 'profile' : 'roadmap')}>Continue →</Button></article><article className="next-card interests-card"><div className="next-icon">✦</div><div><small>YOUR INTERESTS</small><h2>{p.interests || 'Add your learning interests'}</h2><p>We’ll use these to make future recommendations more relevant.</p></div><Button onClick={() => go('profile')}>View profile →</Button></article></section></Shell> }

function Mentor({ page, go }: { page: Page; go: (p: Page) => void }) { const p = getLearner(); const [text, setText] = useState(''); const [messages, setMessages] = useState([{ role: 'ai', text: `Hi ${p.name.split(' ')[0]}! What would you like to learn today?` }, { role: 'user', text: 'What should I focus on this week?' }, { role: 'ai', text: 'Start with neural-network fundamentals and a small PyTorch exercise each day.' }]); 
const send = async () => {
  if (!text.trim()) return;

  const learner = getLearner();

  const roadmap = JSON.parse(
    localStorage.getItem("pathpilot-roadmap") || "{}"
  );

  const prompt = `
User Goal: ${learner.goal}
Experience Level: ${learner.level}
Study Hours: ${learner.hours}

Current Roadmap:
${JSON.stringify(roadmap, null, 2)}

Question:
${text}
`;

  const response = await fetch(
    "http://localhost:8000/ai/chat",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        message: prompt
      })
    }
  );

  const data = await response.json();

  setMessages(prev => [
    ...prev,
    { role: "user", text },
    { role: "ai", text: data.response }
  ]);

  setText("");
};
return <Shell page={page} go={go}><Heading eyebrow="YOUR AI LEARNING COMPANION" title={<>How can I help you <em>grow today?</em></>} /><div className="mentor-layout"><aside className="chat-history-side"><small>RECENT CONVERSATIONS</small><button className="current">This week’s learning plan</button><button>Understanding neural networks</button><button>Preparing for Month 2</button></aside><div className="chat-window"><div className="chat-title"><div className="mentor-icon">✦</div><div><strong>PathPilot Mentor</strong><small>Online · Here to help you learn</small></div></div><div className="chat-history">{messages.map((m, i) => <div className={`bubble-row ${m.role}`} key={i}><div className="bubble-avatar">{m.role === 'ai' ? '✦' : initials(p.name)}</div><div className="chat-bubble">{m.text}</div></div>)}</div><form className="chat-input" onSubmit={e => { e.preventDefault(); send() }}><input value={text} onChange={e => setText(e.target.value)} placeholder="Ask your mentor anything..." /><button>→</button></form></div></div></Shell> }

function App() { const [page, setPage] = useState<Page>(() => (location.hash.slice(1) as Page) || 'landing'); const [, rerender] = useState(0); useEffect(() => { const sync = () => setPage((location.hash.slice(1) as Page) || 'landing'); addEventListener('hashchange', sync); return () => removeEventListener('hashchange', sync) }, []); const go = (p: Page) => location.hash = p; const refresh = () => rerender(x => x + 1); const views: Record<Page, ReactNode> = { landing: <Landing go={go} />, login: <Login go={go} refresh={refresh} />, setup: <Setup go={go} refresh={refresh} />, profile: <Profile page={page} go={go} />, roadmap: <Roadmap page={page} go={go} />, courses: <Courses page={page} go={go} />, course: <CoursePage page={page} go={go}/>, dashboard: <Dashboard page={page} go={go} />, mentor: <Mentor page={page} go={go} /> }; return <>{views[page]}</> }
createRoot(document.getElementById('root')!).render(<App />)
