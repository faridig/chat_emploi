import { render, screen } from '@testing-library/react'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { ChatMessage } from '@/components/ui/chat-message'
import { TimelineProgress } from '@/components/ui/timeline-progress'

describe('UI Components', () => {
  describe('Button', () => {
    it('renders correctly', () => {
      render(<Button>Click me</Button>)
      expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument()
    })

    it('applies variant classes', () => {
      render(<Button variant="destructive">Delete</Button>)
      const button = screen.getByRole('button', { name: /delete/i })
      expect(button).toHaveClass('bg-destructive')
    })
  })

  describe('Card', () => {
    it('renders content correctly', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Card Title</CardTitle>
          </CardHeader>
          <CardContent>Content</CardContent>
        </Card>
      )
      expect(screen.getByText('Card Title')).toBeInTheDocument()
      expect(screen.getByText('Content')).toBeInTheDocument()
    })
  })

  describe('Input', () => {
    it('renders correctly', () => {
      render(<Input placeholder="Type here" />)
      expect(screen.getByPlaceholderText('Type here')).toBeInTheDocument()
    })
  })

  describe('ChatMessage', () => {
    it('renders agent message correctly', () => {
      render(<ChatMessage role="agent" content="Hello user" />)
      expect(screen.getByText('Hello user')).toBeInTheDocument()
    })

    it('renders user message correctly', () => {
      render(<ChatMessage role="user" content="Hi agent" />)
      expect(screen.getByText('Hi agent')).toBeInTheDocument()
    })
  })

  describe('TimelineProgress', () => {
    const steps = [
      { id: '1', label: 'Step 1' },
      { id: '2', label: 'Step 2' },
      { id: '3', label: 'Step 3' },
    ]

    it('renders all steps', () => {
      render(<TimelineProgress steps={steps} currentStepId="2" />)
      expect(screen.getByText('Step 1')).toBeInTheDocument()
      expect(screen.getByText('Step 2')).toBeInTheDocument()
      expect(screen.getByText('Step 3')).toBeInTheDocument()
    })
  })
})
