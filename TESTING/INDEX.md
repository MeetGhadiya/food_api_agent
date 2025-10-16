# 📋 Testing Directory Index

## Overview
Comprehensive test suite for FoodieExpress AI Agent

## Quick Navigation

### 🚀 Getting Started
1. **Read First**: [START_HERE.md](START_HERE.md) - Quick start guide with all essentials
2. **Full Docs**: [README.md](README.md) - Complete documentation

### 🎯 Running Tests
- **Quick Run**: `.\RUN_TESTS.bat` (Windows)
- **Python**: `python run_comprehensive_tests.py`
- **Check Services**: `python check_services.py`

### 📁 Files

| File | Purpose | When to Use |
|------|---------|-------------|
| `START_HERE.md` | Quick start guide | **Start here!** First time setup |
| `README.md` | Full documentation | Reference and troubleshooting |
| `run_comprehensive_tests.py` | Main test suite | Run automated tests |
| `check_services.py` | Health checker | Verify services before testing |
| `RUN_TESTS.bat` | Windows script | Quick one-click test run |

### 🎓 Test Categories (27 Tests Total)

1. **Greetings & Help** (3 tests) - Basic agent responses
2. **Restaurant Discovery** (4 tests) - Search and filtering
3. **Menu & Item Inquiry** (4 tests) - ⚠️ **Critical tests here!**
4. **Context Retention** (2 tests) - Memory across conversations
5. **Ordering Flow** (3 tests) - Order placement
6. **Reviews & Ratings** (2 tests) - Review system
7. **Error Handling** (3 tests) - Edge cases
8. **Multi-Turn Conversations** (3 tests) - Complex flows
9. **Keyword Routing** (3 tests) - Tool selection

### 🔥 Critical Tests

**Must Pass:**
- `AI-003-1`: Item search using primary tool (not cuisine)
- `AI-004-2`: Context retention test
- All AI-007: Error handling tests

### 📊 Success Criteria

- ✅ **90%+** = Excellent
- ⚠️ **70-89%** = Needs work
- ❌ **<70%** = Critical issues

### 🛠️ Prerequisites

Before running tests, ensure:
- [ ] MongoDB running and accessible
- [ ] Ollama service running (`ollama serve`)
- [ ] FastAPI backend on port 8000
- [ ] Flask agent on port 5000

### 📈 Workflow

```
1. Check services → python check_services.py
2. Run tests → python run_comprehensive_tests.py
3. Review results → Check terminal output
4. Fix issues → Update agent/API code
5. Re-test → Verify fixes work
```

### 📝 Results

After each run:
- Terminal shows pass/fail for each test
- JSON file saved: `test_results_YYYYMMDD_HHMMSS.json`
- Summary report with success rate

### 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection error | Start Flask agent |
| 404 errors | Start FastAPI backend |
| Timeout | Check Ollama running |
| Import errors | Install dependencies: `pip install requests` |

### 📚 Related Documents

- **Test Plan**: `../TEST_PLAN_V2.txt` - Full 100+ test plan
- **API Docs**: `../food_api/README.md` - API documentation
- **Agent Docs**: `../food_chatbot_agent/WEB_README.md` - Agent documentation

### 🎯 Next Steps

1. Read [START_HERE.md](START_HERE.md)
2. Run `check_services.py` to verify setup
3. Execute `run_comprehensive_tests.py`
4. Review results and fix any issues
5. Re-run until 90%+ pass rate achieved

---

**Ready to test? Start with [START_HERE.md](START_HERE.md)!** 🚀
