import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Box, AppBar, Toolbar, Typography, IconButton } from '@mui/material';
import { Brightness4, Brightness7 } from '@mui/icons-material';
import { useThemeContext } from './contexts/ThemeContext';

function Dashboard() {
  return <Typography variant="h4">Dashboard</Typography>;
}

function LoginPage() {
  return <Typography variant="h4">Login</Typography>;
}

function AppLayout({ children }: { children: React.ReactNode }) {
  const { mode, toggleTheme } = useThemeContext();

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Wallet
          </Typography>
          <IconButton sx={{ ml: 1 }} onClick={toggleTheme} color="inherit">
            {mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
          </IconButton>
        </Toolbar>
      </AppBar>
      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
        {children}
      </Box>
    </Box>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/*" element={
          <AppLayout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              {/* Add other main app routes here */}
            </Routes>
          </AppLayout>
        } />
      </Routes>
    </Router>
  )
}

export default App 