import { FormEvent, ReactNode, useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

const API = 'http://localhost:8000'

// ── JWT & API Utility ──────────────────────────────────────────────────────────
export const getToken = (): string | null => localStorage.getItem('pathpilot-token')
export const setToken = (t: string) => localStorage.setItem('pathpilot-token', t)
export const clearToken = () => {
  localStorage.removeItem('pathpilot-token')
  localStorage.removeItem('pathpilot-learner')
  localStorage.removeItem('pathpilot-roadmap')
}

export async function apiCall(endpoint: string, options: RequestInit = {}) {
  const token = getToken()
  const res = await fetch(`${API}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers as Record<string, string> || {}),
    },
  })
  if (!res.ok) {
    let msg = 'Request failed'
    try {
      const err = await res.json()
      msg = err.detail || err.message || JSON.stringify(err)
    } catch {
      msg = `HTTP ${res.status}: ${res.statusText}`
    }
    throw new Error(msg)
  }
  return res.json()
}

// ── Types ──────────────────────────────────────────────────────────────────────
type Page = 'landing' | 'login' | 'setup' | 'profile' | 'roadmap' | 'courses' | 'course' | 'dashboard' | 'mentor'
type Learner = { name: string; email: string; goal: string; level: string; hours: string; timeline: string; interests: string; currentSkills: string[] }

const defaultLearner: Learner = {
  name: 'Alex Morgan',
  email: '',
  goal: 'AI Engineer',
  level: 'Intermediate',
  hours: '2 hours',
  timeline: '6 months',
  interests: 'Machine Learning',
  currentSkills: ['Python', 'SQL']
}

const getLearner = (): Learner => {
  try {
    return { ...defaultLearner, ...JSON.parse(localStorage.getItem('pathpilot-learner') || '{}') }
  } catch {
    return defaultLearner
  }
}

const initials = (name: string) =>
  name ? name.split(' ').map(x => x[0]).join('').slice(0, 2).toUpperCase() : 'PP'

// ── Reusable UI Components ───────────────────────────────────────────────────
const Button = ({ children, onClick, kind = 'primary', type = 'button', disabled = false, style }: { children: ReactNode; onClick?: () => void; kind?: 'primary' | 'ghost' | 'outline'; type?: 'button' | 'submit'; disabled?: boolean; style?: React.CSSProperties }) => (
  <button type={type} disabled={disabled} style={style} className={`btn ${kind}`} onClick={onClick}>{children}</button>
)

const Logo = () => (
  <button className="logo" onClick={() => location.hash = 'landing'}>
    <span>✦</span> PathPilot <i>AI</i>
  </button>
)

const GoogleButton = ({ onClick }: { onClick: () => void }) => (
  <button type="button" className="google-btn" onClick={onClick}>
    <b>G</b> Continue with Google
  </button>
)

function Navbar({ go }: { go: (p: Page) => void }) {
  const loggedIn = !!getToken()
  return (
    <header className="navbar">
      <Logo />
      <nav style={{ display: 'flex', gap: '16px' }}>
        <button className="btn ghost" onClick={() => go('roadmap')}>Roadmap</button>
        <button className="btn ghost" onClick={() => go('courses')}>Courses</button>
        <button className="btn ghost" onClick={() => go('mentor')}>AI Mentor</button>
      </nav>
      <div className="nav-actions">
        {loggedIn ? (
          <Button onClick={() => go('dashboard')}>Go to Dashboard →</Button>
        ) : (
          <>
            <Button kind="ghost" onClick={() => go('login')}>Log in</Button>
            <Button onClick={() => go('setup')}>Get started →</Button>
          </>
        )}
      </div>
    </header>
  )
}

function Shell({ page, go, children }: { page: Page; go: (p: Page) => void; children: ReactNode }) {
  const p = getLearner()
  const links: [Page, string, string][] = [
    ['dashboard', '⌂', 'Dashboard'],
    ['profile', '◉', 'My Profile'],
    ['roadmap', '◇', 'Roadmap'],
    ['courses', '▣', 'Courses'],
    ['mentor', '✦', 'AI Mentor']
  ]

  const logout = () => {
    clearToken()
    go('landing')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Logo />
        <div className="side-links">
          {links.map(([id, icon, title]) => (
            <button
              key={id}
              className={page === id ? 'active' : ''}
              onClick={() => go(id)}
            >
              <span>{icon}</span> {title}
            </button>
          ))}
        </div>
        <div className="sidebar-bottom">
          <div className="mini-avatar">{initials(p.name)}</div>
          <div>
            <strong>{p.name}</strong>
            <small>{p.level || 'Learner'}</small>
          </div>
          <button
            onClick={logout}
            style={{ marginLeft: 'auto', background: 'transparent', border: 'none', color: '#94a8c9', cursor: 'pointer', fontSize: '11px' }}
          >
            Log out
          </button>
        </div>
      </aside>
      <main className="app-content">
        <div className="app-top">
          <span className="eyebrow">✦ {p.goal || 'CAREER'} PATHWAY</span>
          <div style={{ display: 'flex', gap: '10px' }}>
            <Button kind="outline" onClick={() => go('profile')}>Profile Settings ⚙</Button>
          </div>
        </div>
        {children}
      </main>
    </div>
  )
}

function Heading({ eyebrow, title, children }: { eyebrow: string; title: ReactNode; children?: ReactNode }) {
  return (
    <section className="page-heading">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        {children}
      </div>
    </section>
  )
}

// ── Landing Page ─────────────────────────────────────────────────────────────
function Landing({ go }: { go: (p: Page) => void }) {
  const features = [
    ['✧', 'AI Skill Gap Analysis', 'Extracts precise missing competencies based on career target.'],
    ['◇', 'Personalized Roadmaps', 'Generates prerequisite-aware topological graph of learning nodes.'],
    ['▣', 'Course Recommendations', 'Curates top Coursera courses tailored for your missing skills.'],
    ['✦', 'AI Mentor & Tutor', 'Context-aware Gemini assistant ready to explain concepts 24/7.'],
    ['◔', 'Progress Tracking', 'Persists progress directly to PostgreSQL for live mastery tracking.']
  ]
  return (
    <div className="landing">
      <Navbar go={go} />
      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow">✦ YOUR PERSONAL AI LEARNING COMPANION</div>
          <h1>Find your path.<br /><em>Build your future.</em></h1>
          <p>PathPilot AI converts your career goals into an adaptive, prerequisite-aware learning roadmap backed by real courses, dynamic progress tracking, and PostgreSQL persistence.</p>
          <div className="hero-actions">
            <Button onClick={() => go('setup')}>Start your journey →</Button>
            <Button kind="ghost" onClick={() => go('login')}>Log in</Button>
          </div>
        </div>
        <div className="hero-visual">
          <div className="orb orb-one" />
          <div className="orb orb-two" />
          <div className="journey-card">
            <div>
              <span className="journey-label">AI ROADMAP ENGINE</span>
              <b>Personalized Career Path</b>
              <small>Prerequisite-Aware Topological DAG</small>
            </div>
            <div className="journey-progress">
              <span>Ready</span>
              <div /><small>PostgreSQL Connected</small>
            </div>
          </div>
        </div>
      </section>
      <section style={{ maxWidth: '1240px', margin: '0 auto 60px', padding: '0 24px', width: '100%' }}>
        <div style={{ textAlign: 'center', marginBottom: '36px' }}>
          <div className="eyebrow">HOW PATHPILOT WORKS</div>
          <h2 style={{ fontSize: '32px' }}>Everything you need to<br /><em style={{ color: '#60a5fa' }}>keep moving forward.</em></h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px' }}>
          {features.map(([icon, title, desc]) => (
            <article key={title} className="dash-card" style={{ padding: '20px' }}>
              <span style={{ fontSize: '24px', color: '#60a5fa', marginBottom: '8px', display: 'block' }}>{icon}</span>
              <h3 style={{ fontSize: '16px', marginBottom: '6px' }}>{title}</h3>
              <p style={{ fontSize: '13px' }}>{desc}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}

// ── Login Page ───────────────────────────────────────────────────────────────
function Login({ go, refresh }: { go: (p: Page) => void; refresh: () => void }) {
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const form = new FormData(e.currentTarget)
    const email = String(form.get('email')).toLowerCase().trim()
    const password = String(form.get('password'))

    try {
      // 1. Authenticate with PostgreSQL backend
      const data = await apiCall('/api/v1/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      })

      setToken(data.access_token)

      // 2. Hydrate profile from DB
      try {
        const prof = await apiCall('/api/v1/profile/me')
        localStorage.setItem('pathpilot-learner', JSON.stringify({
          name: prof.name || email.split('@')[0],
          email: email,
          goal: prof.goal || 'Backend Developer',
          level: prof.experience_level || 'BEGINNER',
          hours: `${prof.study_hours_per_week || 10} hours`,
          timeline: `${prof.timeline_months || 6} months`,
          interests: '',
          currentSkills: (prof.skills || []).map((s: any) => s.name)
        }))
      } catch { }

      // 3. Hydrate roadmap from DB
      try {
        const road = await apiCall('/api/v1/roadmap/current')
        localStorage.setItem('pathpilot-roadmap', JSON.stringify(road))
      } catch { }

      refresh()
      go('dashboard')
    } catch (err: any) {
      setError(err.message || 'Invalid email or password')
    } finally {
      setLoading(false)
    }
  }
  const loginWithGoogle = async () => {
    try {
      const response = await apiCall('/api/v1/auth/google')
      // if (response.ok) {
      if (!response.url) {
        throw new Error('Google authentication URL not received')
      }
      window.location.href = response.url
      refresh()
      go('dashboard')
      // } else {
      //   setError('Google sign-in failed')
      // }
    } catch (err: any) {
      setError(err.message || 'Google sign-in failed')
    }
  }
  return (
    <div className="auth-page-container">
      <div className="auth-card">
        <Logo />
        <div className="auth-symbol" style={{ marginTop: '16px' }}>✦</div>
        <div className="eyebrow">WELCOME BACK</div>
        <h1>Log in to your path.</h1>
        <p style={{ marginBottom: '18px' }}>Use your saved credentials to continue.</p>

        <GoogleButton onClick={() => loginWithGoogle()} />
        <div className="auth-divider"><span>or continue with email</span></div>

        <form onSubmit={submit}>
          <label>Email Address
            <input required name="email" type="email" placeholder="learner@example.com" />
          </label>
          <label>Password
            <input required name="password" type="password" placeholder="Your password" />
          </label>

          {error && <div style={{ color: '#f87171', fontSize: '12px', background: 'rgba(248,113,113,0.1)', padding: '8px 12px', borderRadius: '8px', border: '1px solid rgba(248,113,113,0.3)' }}>{error}</div>}

          <Button type="submit" disabled={loading}>
            {loading ? 'Authenticating with DB...' : 'Log in →'}
          </Button>
        </form>

        <button type="button" className="auth-switch-btn" onClick={() => go('setup')}>
          New to PathPilot? Create an account
        </button>
      </div>
    </div>
  )
}

// ── Setup / Signup & AI Roadmap Generation ──────────────────────────────────
function Setup({ go, refresh }: { go: (p: Page) => void; refresh: () => void }) {
  const [level, setLevel] = useState('Intermediate')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const f = new FormData(e.currentTarget)
    const name = String(f.get('name')).trim()
    const email = String(f.get('email')).toLowerCase().trim()
    const password = String(f.get('password'))
    const goal = String(f.get('goal'))
    const hours = String(f.get('hours'))
    const timeline = String(f.get('timeline'))
    const interests = String(f.get('interests'))
    const currentSkills = String(f.get('skills') || '')
      .split(',')
      .map(s => s.trim())
      .filter(Boolean)

    const hoursNum = parseInt(hours) || 10
    const timelineNum = parseInt(timeline) || 6

    try {
      // 1. Register User in PostgreSQL
      const regData = await apiCall('/api/v1/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          name,
          email,
          password,
          goal,
          experience_level: level.toUpperCase(),
          study_hours_per_week: hoursNum,
          timeline_months: timelineNum,
          current_skills: currentSkills
        })
      })

      if (regData.access_token) {
        setToken(regData.access_token)
      }

      // 2. Generate & Save Roadmap to PostgreSQL (LearningPath & LearningPathNode tables)
      const roadmapData = await apiCall('/ai/generate', {
        method: 'POST',
        body: JSON.stringify({
          user_input: `I want to become a ${goal}. My current level is ${level}. I can study ${hours} daily. My target timeline is ${timeline}.`,
          current_skills: currentSkills
        })
      })

      // 3. Save local caches for responsive rendering
      const profile: Learner = {
        name,
        email,
        goal,
        level,
        hours,
        timeline,
        interests,
        currentSkills
      }

      localStorage.setItem('pathpilot-learner', JSON.stringify(profile))
      localStorage.setItem('pathpilot-roadmap', JSON.stringify(roadmapData))

      refresh()
      go('dashboard')
    } catch (err: any) {
      setError(err.message || 'Registration or Roadmap Generation failed')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="auth-page-container">
        <div className="auth-card" style={{ padding: '48px 32px' }}>
          <Logo />
          <div style={{ margin: '30px 0 20px', display: 'flex', justifyContent: 'center' }}>
            <div style={{ width: '40px', height: '40px', border: '3px solid rgba(96,165,250,0.2)', borderTopColor: '#60a5fa', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
          </div>
          <h2 style={{ fontSize: '20px', marginBottom: '8px' }}>Generating Your Roadmap...</h2>
          <p style={{ fontSize: '13px' }}>Persisting user profile, analyzing skill gaps with Gemini, and saving your DAG to PostgreSQL.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="setup-page" style={{ minHeight: '100vh', background: 'var(--bg-dark)' }}>
      <Navbar go={go} />
      <main style={{ maxWidth: '640px', margin: '40px auto', padding: '0 20px' }}>
        <div className="dash-card" style={{ padding: '36px' }}>
          <div className="eyebrow">✦ START YOUR JOURNEY</div>
          <h1 style={{ fontSize: '28px', marginBottom: '8px' }}>Tell us where you want to <em>go.</em></h1>
          <p style={{ marginBottom: '24px' }}>We will create your account in PostgreSQL and build your personalized learning DAG.</p>

          <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
              Your Name
              <input required name="name" placeholder="e.g. Priya Sharma" style={{ background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '11px 14px', color: '#fff' }} />
            </label>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
              <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
                Email Address
                <input required name="email" type="email" placeholder="you@example.com" style={{ background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '11px 14px', color: '#fff' }} />
              </label>

              <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
                Password
                <input required name="password" type="password" minLength={4} placeholder="••••••••" style={{ background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '11px 14px', color: '#fff' }} />
              </label>
            </div>

            <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
              Career Goal
              <select required name="goal" defaultValue="Backend Developer" style={{ background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '11px 14px', color: '#fff' }}>
                <option>Backend Developer</option>
                <option>AI Engineer</option>
                <option>Data Scientist</option>
                <option>Frontend Developer</option>
                <option>Full Stack Developer</option>
              </select>
            </label>

            <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
              Experience Level
              <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
                {['Beginner', 'Intermediate', 'Advanced'].map(x => (
                  <button
                    key={x}
                    type="button"
                    className={`btn ${x === level ? 'primary' : 'outline'}`}
                    style={{ flex: 1, padding: '8px' }}
                    onClick={() => setLevel(x)}
                  >
                    {x}
                  </button>
                ))}
              </div>
            </label>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
              <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
                Study Hours Per Week
                <select required name="hours" defaultValue="10 hours" style={{ background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '11px 14px', color: '#fff' }}>
                  <option value="5">5 hours</option>
                  <option value="10">10 hours</option>
                  <option value="15">15 hours</option>
                  <option value="20">20+ hours</option>
                </select>
              </label>

              <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
                Target Timeline
                <select required name="timeline" defaultValue="6 months" style={{ background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '11px 14px', color: '#fff' }}>
                  <option value="3">3 months</option>
                  <option value="6">6 months</option>
                  <option value="12">12 months</option>
                </select>
              </label>
            </div>

            <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
              Known Skills (comma separated)
              <input name="skills" placeholder="e.g. Python, SQL, Java" style={{ background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '11px 14px', color: '#fff' }} />
            </label>

            <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
              Special Interests
              <input name="interests" placeholder="e.g. Generative AI, Cloud Architecture" style={{ background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '11px 14px', color: '#fff' }} />
            </label>

            {error && <div style={{ color: '#f87171', fontSize: '12px', background: 'rgba(248,113,113,0.1)', padding: '8px 12px', borderRadius: '8px', border: '1px solid rgba(248,113,113,0.3)' }}>{error}</div>}

            <Button type="submit" kind="primary" style={{ marginTop: '12px', width: '100%', padding: '14px' }}>
              Create Account & Generate Roadmap →
            </Button>

            <button type="button" className="auth-switch-btn" onClick={() => go('login')}>
              Already registered? Log in
            </button>
          </form>
        </div>
      </main>
    </div>
  )
}

// ── Profile Page ─────────────────────────────────────────────────────────────
function Profile({ page, go }: { page: Page; go: (p: Page) => void }) {
  const p = getLearner()
  const roadmapData = JSON.parse(localStorage.getItem('pathpilot-roadmap') || '{}')
  const [profileDb, setProfileDb] = useState<any>(null)
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState('')

  useEffect(() => {
    if (getToken()) {
      apiCall('/api/v1/profile/me')
        .then(data => setProfileDb(data))
        .catch(() => { })
    }
  }, [])

  const currentSkills = profileDb?.skills?.map((s: any) => s.name) || roadmapData?.skill_gap?.current_skills || p.currentSkills || []
  const missingSkills = roadmapData?.skill_gap?.missing_skills || ['Spring Boot', 'REST APIs', 'Docker', 'PostgreSQL']

  const updateProfile = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setSaving(true)
    setMsg('')
    const f = new FormData(e.currentTarget)
    const goal = String(f.get('goal'))
    const hours = parseInt(String(f.get('hours'))) || 10
    const timeline = parseInt(String(f.get('timeline'))) || 6

    try {
      await apiCall('/api/v1/profile/me', {
        method: 'PUT',
        body: JSON.stringify({
          goal,
          study_hours_per_week: hours,
          timeline_months: timeline
        })
      })
      setMsg('Profile successfully updated in PostgreSQL!')
      // Update local cache
      const updated = { ...p, goal, hours: `${hours} hours`, timeline: `${timeline} months` }
      localStorage.setItem('pathpilot-learner', JSON.stringify(updated))
    } catch (err: any) {
      setMsg(`Error: ${err.message}`)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Shell page={page} go={go}>
      <Heading
        eyebrow="YOUR LEARNER PROFILE"
        title={<>Great to meet you, <em>{p.name.split(' ')[0]}.</em></>}
      >
        <p>Managed in PostgreSQL database. Edit your goals and track detected skill gaps below.</p>
      </Heading>

      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '24px', marginBottom: '28px' }}>
        <div className="dash-card">
          <div className="card-header">
            <h3>Career Destination Settings</h3>
            <span className="badge-pill">{p.level}</span>
          </div>

          <form onSubmit={updateProfile} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
              Goal Title
              <input name="goal" defaultValue={p.goal} style={{ background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '10px 14px', color: '#fff' }} />
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
                Study Hours / Week
                <input name="hours" type="number" defaultValue={parseInt(p.hours) || 10} style={{ background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '10px 14px', color: '#fff' }} />
              </label>
              <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
                Timeline (Months)
                <input name="timeline" type="number" defaultValue={parseInt(p.timeline) || 6} style={{ background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '10px 14px', color: '#fff' }} />
              </label>
            </div>

            {msg && <div style={{ fontSize: '12px', color: '#4ade80' }}>{msg}</div>}

            <Button type="submit" disabled={saving}>
              {saving ? 'Saving...' : 'Save Profile Changes →'}
            </Button>
          </form>
        </div>

        <div className="dash-card">
          <div className="card-header">
            <h3>Verified Skills & Gaps</h3>
          </div>
          <h4 style={{ fontSize: '13px', color: '#38ef7d', marginBottom: '8px' }}>✓ Current Foundation</h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '18px' }}>
            {currentSkills.map((s: string) => (
              <span key={s} style={{ background: 'rgba(56,239,125,0.1)', border: '1px solid rgba(56,239,125,0.3)', color: '#38ef7d', padding: '4px 10px', borderRadius: '8px', fontSize: '12px' }}>
                ✓ {s}
              </span>
            ))}
          </div>

          <h4 style={{ fontSize: '13px', color: '#f472b6', marginBottom: '8px' }}>✦ Identified Gaps to Build</h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {missingSkills.map((s: string) => (
              <span key={s} style={{ background: 'rgba(244,114,182,0.1)', border: '1px solid rgba(244,114,182,0.3)', color: '#f472b6', padding: '4px 10px', borderRadius: '8px', fontSize: '12px' }}>
                ◎ {s}
              </span>
            ))}
          </div>
        </div>
      </div>
    </Shell>
  )
}

// ── Roadmap Page ─────────────────────────────────────────────────────────────
function Roadmap({ page, go }: { page: Page; go: (p: Page) => void }) {
  const [roadmapDb, setRoadmapDb] = useState<any>(null)
  const roadmapData = JSON.parse(localStorage.getItem('pathpilot-roadmap') || '{}')

  useEffect(() => {
    if (getToken()) {
      apiCall('/api/v1/roadmap/current')
        .then(data => setRoadmapDb(data))
        .catch(() => { })
    }
  }, [])

  const milestones = roadmapDb?.milestones || []
  const roadmapFallback = roadmapData?.roadmap || {}

  return (
    <Shell page={page} go={go}>
      <Heading
        eyebrow="TOPOLOGICAL ROADMAP DAG"
        title={<>From here to <em>your goal.</em></>}
      >
        <p>Prerequisite-ordered learning milestones saved directly in PostgreSQL.</p>
      </Heading>

      {milestones.length > 0 ? (
        <div className="milestones-timeline">
          {milestones.map((m: any, idx: number) => (
            <div key={m.milestone_id || idx} className="milestone-block">
              <div className="milestone-header">
                <h2>{m.title}</h2>
                <span className="milestone-badge">{m.nodes?.length || 0} Modules</span>
              </div>
              <div className="nodes-flow-grid">
                {m.nodes?.map((node: any) => (
                  <article key={node.node_id} className="node-card">
                    <div className="node-header">
                      <span className="node-type-badge">{node.type}</span>
                      <span className={`node-status-badge status-${node.status?.toLowerCase().replace('_', '-')}`}>
                        {node.status}
                      </span>
                    </div>
                    <h4>{node.title}</h4>
                    <div className="node-footer">
                      <span>⏱ {node.estimated_hours}h</span>
                      {node.resource_url ? (
                        <a href={node.resource_url} target="_blank" rel="noreferrer" style={{ color: '#60a5fa', fontWeight: 600 }}>
                          Launch ↗
                        </a>
                      ) : (
                        <span style={{ color: '#94a8c9' }}>Core Module</span>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : Object.keys(roadmapFallback).length > 0 ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
          {Object.entries(roadmapFallback).map(([month, topics]: any, idx) => (
            <div key={month} className="dash-card">
              <span className="eyebrow">{month.replace('_', ' ').toUpperCase()}</span>
              <h3 style={{ fontSize: '18px', margin: '6px 0 12px' }}>Module {idx + 1}</h3>
              <ul style={{ paddingLeft: '18px', color: 'var(--text-muted)', fontSize: '13px' }}>
                {(Array.isArray(topics) ? topics : []).map((t: string) => (
                  <li key={t} style={{ marginBottom: '4px' }}>{t}</li>
                ))}
              </ul>
              <Button kind="outline" style={{ marginTop: '16px', width: '100%' }} onClick={() => go('courses')}>
                Explore Courses →
              </Button>
            </div>
          ))}
        </div>
      ) : (
        <div className="dash-card" style={{ textAlign: 'center', padding: '40px' }}>
          <h3>No Roadmap Found</h3>
          <p style={{ margin: '8px 0 16px' }}>Complete your onboarding profile to generate an AI roadmap.</p>
          <Button onClick={() => go('setup')}>Generate Roadmap Now →</Button>
        </div>
      )}
    </Shell>
  )
}

// ── Courses Page ─────────────────────────────────────────────────────────────
function Courses({ page, go }: { page: Page; go: (p: Page) => void }) {
  const [courses, setCourses] = useState<any[]>([])

  useEffect(() => {
    fetch('http://localhost:8000/courses/')
      .then(res => res.json())
      .then(data => setCourses(data))
      .catch(() => { })
  }, [])

  return (
    <Shell page={page} go={go}>
      <Heading eyebrow="RECOMMENDED COURSES" title={<>Learn what moves you <em>forward.</em></>}>
        <p>Curated from Coursera catalog to close your specific skill gaps.</p>
      </Heading>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
        {(courses.length > 0 ? courses : [
          { title: 'Python for Beginners to Pro', difficulty: 'BEGINNER', platform: 'Coursera', description: 'Master modern Python syntax, data structures, and APIs.', url: 'https://www.coursera.org' },
          { title: 'FastAPI Masterclass: Modern Async REST APIs', difficulty: 'INTERMEDIATE', platform: 'Coursera', description: 'Build async web services with Pydantic validation & JWT security.', url: 'https://www.coursera.org' },
          { title: 'Spring Boot Fundamentals', difficulty: 'INTERMEDIATE', platform: 'Coursera', description: 'Master Spring Boot autoconfiguration, JPA repositories, and REST controllers.', url: 'https://www.coursera.org' }
        ]).map((c: any) => (
          <article key={c.title} className="dash-card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="badge-pill">{c.difficulty}</span>
              <span style={{ fontSize: '11px', color: '#94a8c9' }}>{c.platform || 'Coursera'}</span>
            </div>
            <h3 style={{ fontSize: '17px' }}>{c.title}</h3>
            <p style={{ fontSize: '13px', flex: 1 }}>{c.description}</p>
            <a href={c.url || 'https://www.coursera.org'} target="_blank" rel="noreferrer" className="btn outline" style={{ marginTop: 'auto', textAlign: 'center' }}>
              View Course on Coursera ↗
            </a>
          </article>
        ))}
      </div>
    </Shell>
  )
}

function CoursePage({ page, go }: { page: Page; go: (p: Page) => void }) {
  return (
    <Shell page={page} go={go}>
      <Heading eyebrow="COURSE DETAILS" title={<>Course Curriculum</>} />
      <div className="dash-card">
        <Button kind="outline" onClick={() => go('courses')}>Back to Courses</Button>
      </div>
    </Shell>
  )
}

// ── Dashboard Page with Real Progress Tracking ──────────────────────────────
function Dashboard({ page, go }: { page: Page; go: (p: Page) => void }) {
  const p = getLearner()
  const [progress, setProgress] = useState<any>(null)
  const [updating, setUpdating] = useState<string | null>(null)

  const loadProgress = () => {
    if (getToken()) {
      apiCall('/api/v1/progress')
        .then(data => setProgress(data))
        .catch(() => { })
    }
  }

  useEffect(() => {
    loadProgress()
  }, [])

  const markSkillComplete = async (skillName: string, currentPct: number) => {
    setUpdating(skillName)
    try {
      const nextPct = currentPct >= 100 ? 0 : Math.min(100, currentPct + 25)
      await apiCall('/api/v1/progress', {
        method: 'POST',
        body: JSON.stringify({
          skill_name: skillName,
          completion_percentage: nextPct
        })
      })
      loadProgress()
    } catch (err) {
      console.warn('Progress update error:', err)
    } finally {
      setUpdating(null)
    }
  }

  const overall = progress?.overall_completion ?? 45.0
  const skillsList = progress?.skills || [
    { skill_name: 'Python', completion_percentage: 80 },
    { skill_name: 'SQL', completion_percentage: 60 },
    { skill_name: 'Spring Boot', completion_percentage: 40 },
    { skill_name: 'Docker', completion_percentage: 20 }
  ]

  return (
    <Shell page={page} go={go}>
      <Heading
        eyebrow="✦ LIVE LEARNING DASHBOARD"
        title={<>Welcome Back, <em>{p.name.split(' ')[0]}.</em></>}
      >
        <p>Goal: {p.goal} · Study Commitment: {p.hours}/week · Timeline: {p.timeline}</p>
      </Heading>

      <div className="dashboard-grid">
        {/* Main Progress Card */}
        <div className="dash-card">
          <div className="card-header">
            <h3>Overall Path Progress</h3>
            <span className="badge-pill">{overall}% Completed</span>
          </div>

          <div className="progress-bar-container">
            <div className="progress-bar-fill" style={{ width: `${overall}%` }} />
          </div>

          <div className="next-action-box">
            <div className="next-action-tag">✦ NEXT RECOMMENDED ACTION</div>
            <h4 style={{ fontSize: '16px', margin: '4px 0 6px' }}>Spring Boot Fundamentals & APIs</h4>
            <p style={{ fontSize: '13px' }}>Continue with Month 1 milestones in your personalized roadmap.</p>
            <div className="action-buttons">
              <Button onClick={() => go('roadmap')}>Open Roadmap Canvas →</Button>
              <Button kind="ghost" onClick={() => go('mentor')}>Ask AI Mentor ✦</Button>
            </div>
          </div>
        </div>

        {/* Live Skill Progress in PostgreSQL */}
        <div className="dash-card">
          <div className="card-header">
            <h3>Tracked Skills Progress</h3>
            <small style={{ color: '#94a8c9' }}>Saved in PostgreSQL</small>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {skillsList.map((s: any) => (
              <div key={s.skill_name} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '13px' }}>
                  <strong>{s.skill_name}</strong>
                  <button
                    onClick={() => markSkillComplete(s.skill_name, s.completion_percentage)}
                    disabled={updating === s.skill_name}
                    style={{ background: 'rgba(96,165,250,0.1)', border: '1px solid rgba(96,165,250,0.3)', color: '#60a5fa', borderRadius: '6px', padding: '2px 8px', fontSize: '11px', cursor: 'pointer' }}
                  >
                    {updating === s.skill_name ? 'Saving...' : `${s.completion_percentage}% (+25%)`}
                  </button>
                </div>
                <div className="progress-bar-container" style={{ margin: '2px 0' }}>
                  <div className="progress-bar-fill" style={{ width: `${s.completion_percentage}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Shell>
  )
}

// ── AI Mentor Chat Page ──────────────────────────────────────────────────────
function Mentor({ page, go }: { page: Page; go: (p: Page) => void }) {
  const p = getLearner()
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<Array<{ role: 'ai' | 'user'; text: string }>>([
    { role: 'ai', text: `Hi ${p.name.split(' ')[0]}! I am your PathPilot AI Mentor. How can I help you with your ${p.goal} journey today?` }
  ])
  const [sending, setSending] = useState(false)

  const send = async (e?: FormEvent) => {
    if (e) e.preventDefault()
    if (!input.trim() || sending) return

    const userText = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: userText }])
    setSending(true)

    try {
      // 1. Try backend RAG mentor chat endpoint with history logging
      const res = await apiCall('/api/v1/chat', {
        method: 'POST',
        body: JSON.stringify({ query: userText })
      })
      setMessages(prev => [...prev, { role: 'ai', text: res.reply || 'Explanation generated.' }])
    } catch {
      // 2. Fallback to direct Gemini flash endpoint
      try {
        const res2 = await apiCall('/ai/chat', {
          method: 'POST',
          body: JSON.stringify({ message: `Goal: ${p.goal}. Question: ${userText}` })
        })
        setMessages(prev => [...prev, { role: 'ai', text: res2.response || 'Answer from mentor.' }])
      } catch (err: any) {
        setMessages(prev => [...prev, { role: 'ai', text: `Mentor Error: ${err.message}` }])
      }
    } finally {
      setSending(false)
    }
  }

  return (
    <Shell page={page} go={go}>
      <Heading eyebrow="AI MENTOR & TUTOR" title={<>How can I help you <em>grow today?</em></>} />

      <div style={{ display: 'grid', gridTemplateColumns: '240px 1fr', gap: '20px', height: '600px' }}>
        {/* Suggested Prompts */}
        <div className="dash-card" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <small className="eyebrow">QUICK QUESTIONS</small>
          {[
            'Explain Spring Boot vs FastAPI',
            'What projects should I build for my portfolio?',
            'How to master SQL indexes and joins?',
            'Review my Month 1 learning schedule'
          ].map(prompt => (
            <button
              key={prompt}
              onClick={() => { setInput(prompt); }}
              className="btn outline"
              style={{ textAlign: 'left', fontSize: '12px', padding: '8px 12px', whiteSpace: 'normal' }}
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Chat History & Input */}
        <div className="dash-card" style={{ display: 'flex', flexDirection: 'column', padding: '0', overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', background: 'var(--bg-card)', borderBottom: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ color: '#60a5fa', fontSize: '18px' }}>✦</span>
            <div>
              <strong>PathPilot Mentor</strong>
              <small style={{ display: 'block', color: '#38ef7d', fontSize: '11px' }}>● Online · Ready to assist</small>
            </div>
          </div>

          <div style={{ flex: 1, padding: '20px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {messages.map((m, i) => (
              <div
                key={i}
                style={{
                  alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
                  background: m.role === 'user' ? '#2563eb' : 'var(--bg-card)',
                  border: m.role === 'user' ? 'none' : '1px solid var(--border-subtle)',
                  color: '#ffffff',
                  padding: '12px 16px',
                  borderRadius: '14px',
                  maxWidth: '80%',
                  fontSize: '13px',
                  lineHeight: '1.5'
                }}
              >
                <div style={{ fontSize: '10px', fontWeight: 700, color: m.role === 'user' ? '#93c5fd' : '#60a5fa', marginBottom: '4px' }}>
                  {m.role === 'user' ? 'YOU' : 'AI MENTOR'}
                </div>
                {m.text}
              </div>
            ))}
            {sending && (
              <div style={{ alignSelf: 'flex-start', color: '#94a8c9', fontSize: '12px' }}>
                AI Mentor is thinking...
              </div>
            )}
          </div>

          <form onSubmit={send} style={{ display: 'flex', gap: '10px', padding: '16px', background: 'var(--bg-card)', borderTop: '1px solid var(--border-subtle)' }}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Ask your mentor anything about code, algorithms, or career paths..."
              style={{ flex: 1, background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '10px 14px', color: '#fff', fontSize: '13px', outline: 'none' }}
            />
            <Button type="submit" disabled={sending || !input.trim()}>
              Send →
            </Button>
          </form>
        </div>
      </div>
    </Shell>
  )
}

// ── Root App Router ──────────────────────────────────────────────────────────
function App() {
  const [page, setPage] = useState<Page>(() => (location.hash.slice(1) as Page) || 'landing')
  const [, rerender] = useState(0)

  useEffect(() => {
    const sync = () => {
      const p = (location.hash.slice(1) as Page) || 'landing'
      setPage(p)
    }
    addEventListener('hashchange', sync)
    return () => removeEventListener('hashchange', sync)
  }, [])

  const go = (p: Page) => {
    location.hash = p
  }

  const refresh = () => rerender(x => x + 1)

  const views: Record<Page, ReactNode> = {
    landing: <Landing go={go} />,
    login: <Login go={go} refresh={refresh} />,
    setup: <Setup go={go} refresh={refresh} />,
    profile: <Profile page={page} go={go} />,
    roadmap: <Roadmap page={page} go={go} />,
    courses: <Courses page={page} go={go} />,
    course: <CoursePage page={page} go={go} />,
    dashboard: <Dashboard page={page} go={go} />,
    mentor: <Mentor page={page} go={go} />
  }

  return <>{views[page] || <Landing go={go} />}</>
}

const rootElement = document.getElementById('root')
if (rootElement) {
  createRoot(rootElement).render(<App />)
}
