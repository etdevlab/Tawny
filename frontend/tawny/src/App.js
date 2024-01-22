import './App.css';
import Login from "./pages/Login";
import {Route, Routes} from "react-router-dom";

function App() {
  //Create routes for the app
  return (
    <Routes>
      <Route exact path="/" element={<Login />} />
      <Route path="/login" element={<Login />} />

      <Route path="*" element={<div>404</div>} />
    </Routes>
  )
}

export default App;