import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import Login from './Login';
import AdminDashboard from './AdminDashboard';
import MarketingDashboard from './MarketingDashboard';

const App = () => {
  const [token, setToken] = useState(null);

  return (
    <Router>
      <Switch>
        <Route path="/login">
          <Login setToken={setToken} />
        </Route>
        <Route path="/admin-dashboard">
          {token ? <AdminDashboard /> : <Redirect to="/login" />}
        </Route>
        <Route path="/marketing-dashboard">
          {token ? <MarketingDashboard /> : <Redirect to="/login" />}
        </Route>
        <Route path="/">
          <Redirect to="/login" />
        </Route>
      </Switch>
    </Router>
  );
};

export default App;