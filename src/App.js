import React from 'react';
import './App.css';
import StatusPanel from './StatusPanel';
import { hot } from 'react-hot-loader/root';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <StatusPanel />
      </header>
    </div>
  );
}

export default hot(App);
