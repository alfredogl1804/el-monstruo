#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# El Monstruo Mobile — Build Script
# ═══════════════════════════════════════════════════════════════════
# Run this on your Mac after Android Studio and Xcode are installed.
# Usage: ./build.sh [android|ios|all]
# ═══════════════════════════════════════════════════════════════════

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  El Monstruo Mobile — Build Script v0.1.0${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

TARGET="${1:-all}"

# ─── Step 1: Check prerequisites ───
echo -e "${YELLOW}[1/6] Checking prerequisites...${NC}"

if ! command -v flutter &> /dev/null; then
    echo -e "${RED}ERROR: Flutter not found. Install with: brew install --cask flutter${NC}"
    exit 1
fi

FLUTTER_VERSION=$(flutter --version 2>/dev/null | head -1)
echo -e "  ${GREEN}✓${NC} $FLUTTER_VERSION"

if [[ "$TARGET" == "ios" || "$TARGET" == "all" ]]; then
    if ! command -v xcodebuild &> /dev/null; then
        echo -e "${RED}ERROR: Xcode not found. Install from App Store.${NC}"
        exit 1
    fi
    XCODE_VERSION=$(xcodebuild -version 2>/dev/null | head -1)
    echo -e "  ${GREEN}✓${NC} $XCODE_VERSION"
fi

if [[ "$TARGET" == "android" || "$TARGET" == "all" ]]; then
    if [ ! -d "$HOME/Library/Android/sdk" ] && [ -z "$ANDROID_HOME" ]; then
        echo -e "${RED}ERROR: Android SDK not found. Open Android Studio to install it.${NC}"
        exit 1
    fi
    echo -e "  ${GREEN}✓${NC} Android SDK found"
fi

# ─── Step 2: Generate native project files ───
echo ""
echo -e "${YELLOW}[2/6] Generating native project files...${NC}"

if [ ! -f "android/build.gradle" ] || [ ! -f "ios/Runner.xcodeproj/project.pbxproj" ]; then
    flutter create . --org com.elmonstruo --project-name el_monstruo \
        --description "El Monstruo — Agente IA Soberano" \
        --platforms android,ios \
        --no-overwrite
    echo -e "  ${GREEN}✓${NC} Native project files generated"
else
    echo -e "  ${GREEN}✓${NC} Native project files already exist"
fi

# ─── Step 3: Install dependencies ───
echo ""
echo -e "${YELLOW}[3/6] Installing dependencies...${NC}"
flutter pub get
echo -e "  ${GREEN}✓${NC} Dependencies installed"

# ─── Step 4: Run analysis ───
echo ""
echo -e "${YELLOW}[4/6] Running code analysis...${NC}"
flutter analyze --no-fatal-infos || true
echo -e "  ${GREEN}✓${NC} Analysis complete"

# ─── Step 5: Build ───
echo ""
echo -e "${YELLOW}[5/6] Building...${NC}"

if [[ "$TARGET" == "android" || "$TARGET" == "all" ]]; then
    echo -e "  ${CYAN}Building Android APK (release)...${NC}"
    flutter build apk --release
    APK_PATH="build/app/outputs/flutter-apk/app-release.apk"
    if [ -f "$APK_PATH" ]; then
        APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
        echo -e "  ${GREEN}✓${NC} Android APK: $APK_PATH ($APK_SIZE)"
    fi
fi

if [[ "$TARGET" == "ios" || "$TARGET" == "all" ]]; then
    echo -e "  ${CYAN}Building iOS (no codesign for now)...${NC}"
    flutter build ios --no-codesign --release
    echo -e "  ${GREEN}✓${NC} iOS build complete (unsigned)"
    echo -e "  ${YELLOW}  → To install on iPhone: open ios/Runner.xcworkspace in Xcode${NC}"
    echo -e "  ${YELLOW}    and run on your device with your Apple ID${NC}"
fi

# ─── Step 6: Summary ───
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  BUILD COMPLETE${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

if [[ "$TARGET" == "android" || "$TARGET" == "all" ]]; then
    echo -e "  ${GREEN}Android APK:${NC} $APK_PATH"
    echo -e "  ${YELLOW}Install:${NC} adb install $APK_PATH"
    echo -e "  ${YELLOW}Or:${NC} Transfer APK to Samsung S26 Ultra / OPPO Find N5"
fi

if [[ "$TARGET" == "ios" || "$TARGET" == "all" ]]; then
    echo ""
    echo -e "  ${GREEN}iOS:${NC} Open ios/Runner.xcworkspace in Xcode"
    echo -e "  ${YELLOW}Steps:${NC}"
    echo -e "    1. Select your iPhone 17 Pro as target device"
    echo -e "    2. Sign with your Apple ID (free or paid)"
    echo -e "    3. Click Run (▶)"
fi

echo ""
echo -e "  ${CYAN}Gateway:${NC} Deploy apps/mobile/gateway/ to Railway"
echo -e "  ${CYAN}Kernel:${NC} $KERNEL_URL"
echo ""
