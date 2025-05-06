import UserFetcher from './components/UserFetcher'
import './App.css'
import Chatbot from './components/Chatbot';

const App: React.FC = () => {
  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>Axios HTTP 호출 테스트</h1>
      <Chatbot />
    </div>
  );
}

export default App
