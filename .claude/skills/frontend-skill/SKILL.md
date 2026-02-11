---
name: frontend-skill
description: Build responsive pages, reusable components, layouts, and styling for a Next.js App Router application.
---

# Frontend Skill

## Instructions

1. **Page construction**
   - Build pages using Next.js App Router conventions
   - Organize routes and layouts clearly
   - Support dynamic and static pages
   - Ensure pages are SEO-friendly and accessible

2. **Component design**
   - Create reusable UI components (buttons, forms, cards, lists)
   - Keep components small and composable
   - Separate presentational and logic-based components
   - Ensure consistency across the application

3. **Layout management**
   - Define global and nested layouts
   - Use responsive grid or flexbox layouts
   - Maintain consistent spacing and alignment
   - Support mobile, tablet, and desktop views

4. **Styling**
   - Apply modern styling using Tailwind CSS or CSS modules
   - Ensure high-contrast and readable typography
   - Maintain a consistent design system
   - Support dark/light modes if applicable

5. **Integration**
   - Connect UI components to backend APIs
   - Handle loading, error, and empty states
   - Integrate authentication-aware UI elements
   - Expose reusable frontend building blocks for agents

## Best Practices
- Mobile-first design approach
- Reuse components instead of duplicating UI
- Keep styling consistent and minimal
- Ensure accessibility (ARIA labels, keyboard navigation)
- Optimize components for performance and clarity

## Example Structure
```tsx
export function Layout({ children }) {
  return (
    <main className="min-h-screen p-4">
      {children}
    </main>
  )
}

export function Page() {
  return (
    <section className="max-w-4xl mx-auto">
      <h1 className="text-xl font-bold">Page Title</h1>
      <p className="text-muted">Page content goes here</p>
    </section>
  )
}