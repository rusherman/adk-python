# React Skill

A comprehensive React development skill covering fundamentals, hooks, components, and best practices.

## Core Concepts

### Components

**Function Components (Recommended)**
```jsx
function Welcome(props) {
  return <h1>Hello, {props.name}!</h1>;
}

// Arrow function syntax
const Welcome = ({ name }) => {
  return <h1>Hello, {name}!</h1>;
};

// Implicit return
const Welcome = ({ name }) => <h1>Hello, {name}!</h1>;
```

**Class Components (Legacy)**
```jsx
class Welcome extends React.Component {
  render() {
    return <h1>Hello, {this.props.name}!</h1>;
  }
}
```

### JSX Syntax

```jsx
// Basic JSX
const element = <h1>Hello, world!</h1>;

// JSX with expressions
const name = 'John';
const element = <h1>Hello, {name}!</h1>;

// JSX with attributes
const element = <div className="container" id="main">Content</div>;

// JSX with children
const element = (
  <div>
    <h1>Title</h1>
    <p>Paragraph</p>
  </div>
);
```

## Hooks

### useState

```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  );
}
```

### useEffect

```jsx
import { useState, useEffect } from 'react';

function DataFetcher() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Component did mount + update
    fetchData();

    // Cleanup function (component will unmount)
    return () => {
      // Cleanup logic here
    };
  }, []); // Empty dependency array = run once

  async function fetchData() {
    try {
      const response = await fetch('/api/data');
      const result = await response.json();
      setData(result);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div>Loading...</div>;
  return <div>Data: {JSON.stringify(data)}</div>;
}
```

### useContext

```jsx
import { createContext, useContext, useState } from 'react';

const ThemeContext = createContext();

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

function ThemedButton() {
  const { theme, setTheme } = useContext(ThemeContext);

  return (
    <button
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
      className={`btn-${theme}`}
    >
      Toggle Theme
    </button>
  );
}
```

### useReducer

```jsx
import { useReducer } from 'react';

function reducer(state, action) {
  switch (action.type) {
    case 'increment':
      return { count: state.count + 1 };
    case 'decrement':
      return { count: state.count - 1 };
    case 'reset':
      return { count: 0 };
    default:
      throw new Error();
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, { count: 0 });

  return (
    <div>
      <p>Count: {state.count}</p>
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
      <button onClick={() => dispatch({ type: 'decrement' })}>-</button>
      <button onClick={() => dispatch({ type: 'reset' })}>Reset</button>
    </div>
  );
}
```

### Custom Hooks

```jsx
import { useState, useEffect } from 'react';

function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue];
}

// Usage
function App() {
  const [name, setName] = useLocalStorage('name', '');

  return (
    <input
      value={name}
      onChange={(e) => setName(e.target.value)}
      placeholder="Enter your name"
    />
  );
}
```

## Component Patterns

### Higher-Order Components (HOC)

```jsx
function withLoading(Component) {
  return function WithLoadingComponent({ isLoading, ...props }) {
    if (isLoading) {
      return <div>Loading...</div>;
    }
    return <Component {...props} />;
  };
}

// Usage
const UserProfileWithLoading = withLoading(UserProfile);
```

### Render Props

```jsx
function MouseTracker({ render }) {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      setPosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return render(position);
}

// Usage
function App() {
  return (
    <MouseTracker
      render={({ x, y }) => (
        <div>
          Mouse position: {x}, {y}
        </div>
      )}
    />
  );
}
```

### Compound Components

```jsx
const Tabs = ({ children }) => {
  const [activeIndex, setActiveIndex] = useState(0);

  return (
    <div className="tabs">
      {React.Children.map(children, (child, index) =>
        React.cloneElement(child, {
          isActive: index === activeIndex,
          onSelect: () => setActiveIndex(index)
        })
      )}
    </div>
  );
};

const Tab = ({ isActive, onSelect, children }) => (
  <button
    className={isActive ? 'tab active' : 'tab'}
    onClick={onSelect}
  >
    {children}
  </button>
);

// Usage
function App() {
  return (
    <Tabs>
      <Tab>First</Tab>
      <Tab>Second</Tab>
      <Tab>Third</Tab>
    </Tabs>
  );
}
```

## State Management

### Lazy Initial State

```jsx
function ExpensiveComponent() {
  const [data, setData] = useState(() => {
    // This function runs only once during initial render
    const expensiveValue = calculateExpensiveValue();
    return expensiveValue;
  });

  // ...
}
```

### Functional Updates

```jsx
function Counter() {
  const [count, setCount] = useState(0);

  const increment = () => {
    setCount(prevCount => prevCount + 1);
    setCount(prevCount => prevCount + 1); // Batch updates
  };

  return <button onClick={increment}>Count: {count}</button>;
}
```

## Performance Optimization

### React.memo

```jsx
const ExpensiveComponent = React.memo(function ExpensiveComponent({ data }) {
  // Component logic
  return <div>{data}</div>;
});

// Custom comparison function
const CustomMemoComponent = React.memo(
  ExpensiveComponent,
  (prevProps, nextProps) => {
    return prevProps.id === nextProps.id;
  }
);
```

### useMemo

```jsx
function ExpensiveCalculation({ items }) {
  const sortedItems = useMemo(() => {
    return items.sort((a, b) => a.value - b.value);
  }, [items]); // Only recalculate when items change

  return <div>{sortedItems.map(item => <div key={item.id}>{item.name}</div>)}</div>;
}
```

### useCallback

```jsx
function ParentComponent() {
  const [count, setCount] = useState(0);

  const handleClick = useCallback(() => {
    setCount(c => c + 1);
  }, []); // Function identity is stable

  return <ChildComponent onClick={handleClick} />;
}

const ChildComponent = React.memo(({ onClick }) => {
  return <button onClick={onClick}>Click me</button>;
});
```

## Error Handling

### Error Boundaries

```jsx
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <h1>Something went wrong.</h1>;
    }

    return this.props.children;
  }
}

// Usage
function App() {
  return (
    <ErrorBoundary fallback={<div>Error occurred!</div>}>
      <MyComponent />
    </ErrorBoundary>
  );
}
```

## Testing

### Basic Component Test

```jsx
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

function Counter() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}

describe('Counter', () => {
  test('renders with initial count', () => {
    render(<Counter />);
    expect(screen.getByText(/count: 0/i)).toBeInTheDocument();
  });

  test('increments count on button click', async () => {
    const user = userEvent.setup();
    render(<Counter />);

    const button = screen.getByRole('button', { name: /increment/i });
    await user.click(button);

    expect(screen.getByText(/count: 1/i)).toBeInTheDocument();
  });
});
```

## Best Practices

1. **Component Structure**: Keep components small and focused
2. **Props**: Use descriptive prop names, avoid boolean props when possible
3. **State**: Lift state up when multiple components need the same data
4. **Effects**: Always specify dependencies, cleanup side effects
5. **Performance**: Use React.memo, useMemo, and useCallback appropriately
6. **Testing**: Write tests for critical functionality
7. **Error Handling**: Use error boundaries for graceful error handling
8. **Accessibility**: Use semantic HTML and proper ARIA attributes

## Common Patterns

- **Container/Presentational Components**: Separate logic from presentation
- **Custom Hooks**: Reuse stateful logic across components
- **Context API**: Share data without prop drilling
- **Portals**: Render children into a DOM node outside parent hierarchy
- **Refs**: Access DOM elements or store mutable values

This skill provides a comprehensive foundation for React development, covering modern patterns and best practices.