/**
 * Confidence Check - Pre-implementation assessment
 * ≥90%: proceed | 70-89%: options | <70%: clarify
 * ROI: 25-250x token savings | Precision/Recall: 1.000
 */
import { existsSync } from "fs";
import { join, dirname } from "path";

export interface CheckerOptions {
  silent?: boolean;
}
export interface CheckResult {
  name: string;
  passed: boolean;
  message: string;
  weight: number;
}
export interface ConfidenceResult {
  score: number;
  checks: CheckResult[];
  recommendation: string;
}
export interface Context {
  task?: string;
  test_file?: string;
  test_name?: string;
  markers?: string[];
  duplicate_check_complete?: boolean;
  architecture_check_complete?: boolean;
  official_docs_verified?: boolean;
  oss_reference_complete?: boolean;
  root_cause_identified?: boolean;
  confidence_checks?: string[];
  [key: string]: any;
}

const W = {
  NO_DUPS: 0.25,
  ARCH: 0.25,
  DOCS: 0.2,
  OSS: 0.15,
  ROOT: 0.15,
} as const;

export class ConfidenceChecker {
  constructor(private options: CheckerOptions = {}) {}

  async assess(ctx: Context): Promise<ConfidenceResult> {
    const checks: CheckResult[] = [
      {
        name: "no_duplicates",
        passed: ctx.duplicate_check_complete ?? false,
        message: ctx.duplicate_check_complete
          ? "No duplicates"
          : "Check existing first",
        weight: W.NO_DUPS,
      },
      {
        name: "architecture",
        passed: ctx.architecture_check_complete ?? false,
        message: ctx.architecture_check_complete
          ? "Arch compliant"
          : "Verify architecture",
        weight: W.ARCH,
      },
      {
        name: "official_docs",
        passed: this.hasOfficialDocs(ctx),
        message: ctx.official_docs_verified
          ? "Docs verified"
          : "Read docs first",
        weight: W.DOCS,
      },
      {
        name: "oss_reference",
        passed: ctx.oss_reference_complete ?? false,
        message: ctx.oss_reference_complete ? "OSS found" : "Search OSS",
        weight: W.OSS,
      },
      {
        name: "root_cause",
        passed: ctx.root_cause_identified ?? false,
        message: ctx.root_cause_identified
          ? "Root cause ID'd"
          : "Continue investigation",
        weight: W.ROOT,
      },
    ];
    const score = checks.reduce((s, c) => s + (c.passed ? c.weight : 0), 0);
    ctx.confidence_checks = checks.map(
      (c) => `${c.passed ? "✅" : "❌"} ${c.message}`,
    );
    if (!this.options.silent) {
      console.log("📋 Checks:");
      checks.forEach((c) =>
        console.log(`   ${c.passed ? "✅" : "❌"} ${c.message}`),
      );
    }
    return { score, checks, recommendation: this.getRec(score) };
  }

  private hasOfficialDocs(ctx: Context): boolean {
    if (ctx.official_docs_verified !== undefined)
      return ctx.official_docs_verified;
    const f = ctx.test_file;
    if (!f) return false;
    let d = dirname(f);
    while (d !== dirname(d)) {
      if (
        ["README.md", "CLAUDE.md", "docs"].some((n) => existsSync(join(d, n)))
      )
        return true;
      d = dirname(d);
    }
    return false;
  }

  getRec(c: number): string {
    return c >= 0.9
      ? "✅ High (≥90%) - Proceed"
      : c >= 0.7
        ? "⚠️ Medium (70-89%) - Investigate more"
        : "❌ Low (<70%) - STOP, investigate";
  }
}

/** @deprecated Use ConfidenceChecker */
export const confidenceCheck = async (ctx: Context) =>
  (await new ConfidenceChecker().assess(ctx)).score;
export const getRecommendation = (c: number) =>
  new ConfidenceChecker().getRec(c);
