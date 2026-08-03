# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x     | ✅ Yes             |
| < 2.0   | ❌ No              |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability, please report it via one of the following:

1. **GitHub Private Vulnerability Reporting** (preferred):
   - Go to the [Security tab](https://github.com/Shreya15err2/AI-Learning-Assistant/security) → "Report a vulnerability"

2. **Email**: Contact the maintainer directly through their GitHub profile.

### What to include

- Description of the vulnerability
- Steps to reproduce (proof of concept if available)
- Potential impact assessment
- Any suggested fixes

### What to expect

- **Acknowledgement** within 48 hours
- **Status update** within 5 business days
- Credit in the changelog if you wish

## Known Security Considerations

### User Data

- Passwords are hashed with **bcrypt** (work factor 12)
- JWTs are signed with HS256; the secret key **must** be set via the `JWT_SECRET` environment variable
- User data is stored in `users.json` — this file is gitignored and must never be committed

### File Upload

- Only `.pdf` files are accepted (extension + MIME validation)
- File size is limited by `MAX_UPLOAD_MB` (default: 25 MB)
- Filenames are sanitized to prevent path traversal
- Uploaded files are stored in `backend/uploads/` which is gitignored

### API Security

- CORS is restricted to explicit allowed origins (not `*`)
- No user-uploaded content is executed
- All Pydantic inputs are validated before processing

### Deployment

- Never expose `users.json` or `backend/uploads/` publicly
- Always set a strong `JWT_SECRET` in production (see `.env.example`)
- Always set `GEMINI_API_KEY` as a secret environment variable, not in code
