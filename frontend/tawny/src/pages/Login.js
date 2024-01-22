import React from "react";
import "./Login.css";

function Login(){
    const [username, setUsername] = React.useState("");
    const [password, setPassword] = React.useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log(username, password);
    }

    return (
        <div className="login_page">  
            <form id="loginBox" onSubmit={handleSubmit}>
                <h1 id="loginTitle">Login</h1>
                
                <div className="loginInput">Username: <input 
                    type="text" 
                    onChange={(e) => setUsername(e.target.value)}
                    value={username}
                    required
                />
                </div>
                <div className="loginInput">Password: <input 
                    type="password"
                    onChange={(e) => setPassword(e.target.value)}
                    value={password}
                    required
                />
                </div>
                <button id="loginButton" type="submit">Login</button>
            </form>
        </div>
    );
}

export default Login;