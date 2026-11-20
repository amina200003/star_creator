import Intro from './pages/intro'

export default function App() {
  const handleStart = () => {
    console.log('Navigating to Auth / Dashboard...')
  }

  return <Intro onStart={handleStart} />
}