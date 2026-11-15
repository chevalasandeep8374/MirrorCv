/**
 * Integration and unit test suite for Step 3: ResumeRepository data layer
 * Tests LocalStorageRepository (with optimistic locking & conflict handling)
 * Tests SupabaseRepository (live against Supabase with real auth, optimistic lock RPC, and idempotent import)
 */

import { LocalStorageRepository } from '../src/repositories/LocalStorageRepository';
import { SupabaseRepository } from '../src/repositories/SupabaseRepository';
import { VersionConflictError } from '../src/repositories/ResumeRepository';
import { supabase } from '../src/lib/supabase';

// Mock localStorage for Node environment
class MockLocalStorage {
  private store: Record<string, string> = {};

  getItem(key: string): string | null {
    return this.store[key] ?? null;
  }
  setItem(key: string, value: string): void {
    this.store[key] = value;
  }
  removeItem(key: string): void {
    delete this.store[key];
  }
  clear(): void {
    this.store = {};
  }
}

// Attach mock window/localStorage if running in Node
if (typeof (global as any).window === 'undefined') {
  (global as any).window = {
    localStorage: new MockLocalStorage(),
  };
}

async function runTests() {
  console.log('--- Step 3: ResumeRepository Test Suite ---');
  let passed = 0;
  let failed = 0;

  function assert(condition: boolean, msg: string) {
    if (!condition) {
      console.error(`  FAIL: ${msg}`);
      failed++;
      throw new Error(`Assertion failed: ${msg}`);
    } else {
      console.log(`  PASS: ${msg}`);
      passed++;
    }
  }

  // 1. LocalStorageRepository Unit Tests
  console.log('\n[Group 1] LocalStorageRepository Tests:');
  const localRepo = new LocalStorageRepository();
  localRepo.clear();

  assert(localRepo.hasResumes() === false, 'LocalStorage initially empty');
  const list0 = await localRepo.list(false);
  assert(list0.length === 0, 'list() returns empty array');

  // Create
  const created = await localRepo.create({
    title: 'Local Test Resume',
    target_job_title: 'Software Engineer',
  });
  assert(Boolean(created.id), 'create() returns resume with id');
  assert(created.title === 'Local Test Resume', 'create() sets correct title');
  assert(created.version === 1, 'create() initializes version to 1');
  assert(localRepo.hasResumes() === true, 'hasResumes() returns true after creation');

  // Get
  const fetched = await localRepo.get(created.id);
  assert(fetched !== null && fetched.id === created.id, 'get() retrieves stored resume');

  // Optimistic Locking Update - Success
  const updated1 = await localRepo.update(created.id, {
    title: 'Local Test Resume (V2)',
    expected_version: 1,
  });
  assert(updated1.version === 2, 'update() with matching version increments version to 2');
  assert(updated1.title === 'Local Test Resume (V2)', 'update() applies payload changes');

  // Optimistic Locking Update - Conflict Detection
  let caughtConflict = false;
  try {
    await localRepo.update(created.id, {
      title: 'Conflicting Edit',
      expected_version: 1, // Stale version, current is 2!
    });
  } catch (err: any) {
    if (err instanceof VersionConflictError) {
      caughtConflict = true;
    }
  }
  assert(caughtConflict, 'update() with stale expected_version throws VersionConflictError');

  // Duplicate
  const duplicated = await localRepo.duplicate(created.id);
  assert(duplicated.id !== created.id, 'duplicate() generates a unique ID');
  assert(duplicated.title.includes('(Copy)'), 'duplicate() adds (Copy) suffix');
  assert(duplicated.version === 1, 'duplicate() resets version to 1');

  // Delete
  await localRepo.delete(duplicated.id);
  const remaining = await localRepo.list(false);
  assert(remaining.length === 1, 'delete() properly removes duplicated item');

  // 2. SupabaseRepository Integration Tests (Live against mirrorcv project)
  console.log('\n[Group 2] SupabaseRepository Live Integration Tests:');
  const testEmail = 'alpha_tester_1234@gmail.com';
  const testPassword = 'Password123!';

  const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
    email: testEmail,
    password: testPassword,
  });

  if (authError || !authData.session) {
    throw new Error(`Failed to authenticate with Supabase: ${authError?.message}`);
  }
  console.log(`  Authenticated as ${testEmail} (${authData.user.id})`);

  const supabaseRepo = new SupabaseRepository();

  // Create in Cloud
  const cloudResume = await supabaseRepo.create({
    title: 'Cloud Integration Resume',
    targetJobTitle: 'Full-stack Engineer',
  });
  assert(Boolean(cloudResume.id), 'supabaseRepo.create() creates cloud row');
  assert(cloudResume.version === 1, 'cloud row initializes version to 1');

  // Get from Cloud
  const fetchedCloud = await supabaseRepo.get(cloudResume.id);
  assert(fetchedCloud.title === 'Cloud Integration Resume', 'supabaseRepo.get() retrieves cloud resume');

  // Optimistic lock update on Cloud (via update_resume_optimistic RPC)
  const cloudUpdated = await supabaseRepo.update(cloudResume.id, {
    title: 'Cloud Integration Resume (Updated)',
    expected_version: 1,
  });
  assert(cloudUpdated.version === 2, 'Cloud update increments version atomically to 2');

  // Cloud conflict test
  let cloudConflictCaught = false;
  try {
    await supabaseRepo.update(cloudResume.id, {
      title: 'Cloud Stale Edit',
      expected_version: 1, // Current is 2
    });
  } catch (err: any) {
    if (err instanceof VersionConflictError || err?.code === 'VERSION_CONFLICT') {
      cloudConflictCaught = true;
    }
  }
  assert(cloudConflictCaught, 'Cloud update with stale expected_version throws VersionConflictError');

  // Idempotent Local Resume Import Test
  console.log('\n[Group 3] Idempotent Local Resume Import Test:');
  const localResumesToImport = localRepo.getAll();
  assert(localResumesToImport.length > 0, 'Local resumes prepared for import');

  // 1st Import Run
  const importResult1 = await supabaseRepo.importLocalResumes(localResumesToImport);
  console.log(`  Run 1: imported=${importResult1.importedCount}, skipped=${importResult1.skippedCount}`);
  assert(importResult1.importedCount >= 1, 'First import imports local resume(s)');

  // 2nd Import Run with identical data (must be idempotent and skip without error)
  const importResult2 = await supabaseRepo.importLocalResumes(localResumesToImport);
  console.log(`  Run 2: imported=${importResult2.importedCount}, skipped=${importResult2.skippedCount}`);
  assert(importResult2.importedCount === 0, 'Second import imports 0 duplicate resumes');
  assert(importResult2.skippedCount >= 1, 'Second import skips existing resumes idempotently');

  // Cleanup cloud resumes created during test
  await supabaseRepo.delete(cloudResume.id);
  // Clean up imported test resume by title
  const { data: cleanRows } = await supabase
    .from('resumes')
    .select('id')
    .eq('title', 'Local Test Resume (V2)');
  for (const r of cleanRows || []) {
    await supabaseRepo.delete(r.id);
  }
  console.log('  Cleaned up temporary cloud test rows.');

  console.log(`\n========================================`);
  console.log(`Step 3 Test Results: ${passed} passed, ${failed} failed`);
  console.log(`========================================\n`);
}

runTests().catch((err) => {
  console.error('Test suite failed:', err);
  process.exit(1);
});
