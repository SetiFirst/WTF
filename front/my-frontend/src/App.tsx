import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Auth from './pages/Auth';
import Choice from './pages/Choice';
import RegisterAsPerson from './pages/RegisterAsPerson';
import RegisterAsCompany from './pages/RegisterAsCompany';
import AllCources from './pages/AllCources';
import AppPage from './pages/AppPage';
import Settings from './pages/Settings';
import Course from './pages/Course';


function App() {

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Auth />} />
        <Route path="/choice" element={<Choice />} />
        <Route path="register-as-person" element={<RegisterAsPerson />} />
        <Route path="register-as-company" element={<RegisterAsCompany />} />
        <Route path="/app" element={<AppPage />}>
          <Route path="all-courses" element={<AllCources />} />
          <Route path="settings" element={<Settings />} />
          <Route path="course" element={<Course />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;

