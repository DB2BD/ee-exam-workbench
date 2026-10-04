// src/domain/numericVerifier.js
/**
 * Fast Numeric Verifier for Engineering Exam Solutions
 * ===================================================
 * Compares examinee's calculated final answer against mathematical solutions.
 * Detects common engineering exam pitfalls:
 * 1. Missing / extra sqrt(3) (line vs phase factor ~1.732)
 * 2. Missing / extra 1000x unit prefixes (kilo, milli)
 * 3. Sign inversion (negative sign error)
 * 4. High accuracy match (<= 2.5% tolerance)
 */

function extractNumbersFromText(text) {
  if (!text || typeof text !== 'string') return [];
  // Match numbers including decimals and scientific notation
  const regex = /[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?/g;
  const matches = text.match(regex);
  if (!matches) return [];
  return matches
    .map(Number)
    .filter(n => Number.isFinite(n) && Math.abs(n) > 0.0001);
}

function verifyNumericAnswer(userInput, solutionText) {
  if (userInput === undefined || userInput === null) {
    return { ok: false, matchType: 'empty', message: '請輸入計算數值。' };
  }
  const cleanInput = String(userInput).trim().replace(/,/g, '');
  const userNum = parseFloat(cleanInput);
  if (isNaN(userNum)) {
    return { ok: false, matchType: 'invalid', message: '請輸入有效的數值格式。' };
  }

  const solutionNumbers = extractNumbersFromText(solutionText);
  if (solutionNumbers.length === 0) {
    return { ok: false, matchType: 'no_numbers', message: '本題詳解中未檢索到可用於比對的數值。' };
  }

  const userAbs = Math.abs(userNum);

  // 1. Check for direct match (tolerance <= 3.0%)
  for (const solNum of solutionNumbers) {
    const solAbs = Math.abs(solNum);
    const diffRatio = Math.abs(userAbs - solAbs) / Math.max(solAbs, 0.001);
    if (diffRatio <= 0.03) {
      if (Math.sign(userNum) !== Math.sign(solNum) && solNum !== 0) {
        return {
          ok: false,
          matchType: 'sign_error',
          matchedVal: solNum,
          message: `⚠️ 數值大小正確（${solAbs}），但「正負號相反」！請檢查參考方向定義（如流入／流出、吸收／提供）。`
        };
      }
      return {
        ok: true,
        matchType: 'exact',
        matchedVal: solNum,
        message: `🎉 數值完全命中（約 ${solNum}）！運算精確無誤，請繼續保持！`
      };
    }
  }

  // 2. Check for sqrt(3) factor (~1.732) error (3-phase line vs phase mistake)
  const SQRT3 = Math.sqrt(3);
  for (const solNum of solutionNumbers) {
    const solAbs = Math.abs(solNum);
    const ratio = userAbs / solAbs;
    if (Math.abs(ratio - SQRT3) < 0.06 || Math.abs(ratio - (1 / SQRT3)) < 0.03) {
      return {
        ok: false,
        matchType: 'sqrt3_trap',
        matchedVal: solNum,
        message: `⚠️ 數值偏差約 1.732 倍！強烈提醒：檢查是否漏乘或多除了三相「根號三（√3）」線／相轉換！`
      };
    }
  }

  // 3. Check for 1000x factor error (kilo / milli prefix)
  for (const solNum of solutionNumbers) {
    const solAbs = Math.abs(solNum);
    const ratio = userAbs / solAbs;
    if (Math.abs(ratio - 1000) < 5 || Math.abs(ratio - 0.001) < 0.00005) {
      return {
        ok: false,
        matchType: 'unit_prefix_trap',
        matchedVal: solNum,
        message: `⚠️ 數值偏差 1000 倍！提示：注意單位前綴（如 W 與 kW、V 與 kV、A 與 mA）。`
      };
    }
  }

  return {
    ok: false,
    matchType: 'mismatch',
    message: `🤔 數值未在標準答案中找到相符項。建議點擊下方步驟逐步對照公式與推導。`
  };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    extractNumbersFromText,
    verifyNumericAnswer
  };
}
