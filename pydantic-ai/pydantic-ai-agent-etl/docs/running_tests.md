# Running Tests

This project includes test scripts for both Windows (PowerShell) and Linux environments.

## Windows (PowerShell)

Run tests using `runtest.ps1`:

```powershell
# Run all tests
.\runtest.ps1

# List available tests
.\runtest.ps1 -list

# Run specific test(s)
.\runtest.ps1 -run "test_name"

# Show help
.\runtest.ps1 -help
```

## Linux

Run tests using `runtest.sh`:

```bash
# Run all tests
./runtest.sh

# List available tests
./runtest.sh -l

# Run specific test(s)
./runtest.sh -r "test_name"

# Show help
./runtest.sh -h
```

Both scripts will:
1. Create a Python virtual environment if it doesn't exist
2. Install required test dependencies
3. Run the specified tests
4. Clean up by deactivating the virtual environment