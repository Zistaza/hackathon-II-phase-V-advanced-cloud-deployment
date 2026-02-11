# Data Model: Professional Home Page UI/UX for Todo Web Application

## Theme State Entity

**Entity Name**: ThemeState
- **Fields**:
  - `mode`: string (light|dark) - Current theme mode
  - `isSystemPreferred`: boolean - Whether the theme follows system preference
  - `lastUpdated`: Date - Timestamp of last theme change
- **Validation Rules**:
  - `mode` must be either "light" or "dark"
  - `isSystemPreferred` must be boolean
- **State Transitions**:
  - Initial: detect system preference -> set mode
  - User action: toggle theme -> switch mode
  - System change: OS theme change -> update if isSystemPreferred

## Feature Card Entity

**Entity Name**: FeatureCard
- **Fields**:
  - `id`: string - Unique identifier for the card
  - `title`: string - Feature title (max 50 characters)
  - `description`: string - Feature description (max 150 characters)
  - `icon`: string - Icon identifier or path
  - `order`: number - Display order position
- **Validation Rules**:
  - `title` required, length 1-50 characters
  - `description` required, length 1-150 characters
  - `icon` optional, valid icon identifier
  - `order` required, positive integer
- **Relationships**:
  - Belongs to homepage section

## CTA Button Entity

**Entity Name**: CtaButton
- **Fields**:
  - `id`: string - Unique identifier for the button
  - `label`: string - Button text
  - `variant`: string (primary|secondary) - Visual style
  - `action`: string - Navigation destination
  - `isExternal`: boolean - Whether the link is external
- **Validation Rules**:
  - `label` required, length 1-30 characters
  - `variant` must be "primary" or "secondary"
  - `action` required, valid path or URL
- **Relationships**:
  - Part of authentication section