import UserFetcher from './components/UserFetcher'
import './App.css'

const App: React.FC = () => {
  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>Axios HTTP 호출 테스트</h1>
      <UserFetcher />
    </div>
  );
}

export default App
