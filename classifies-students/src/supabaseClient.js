import { createClient } from '@supabase/supabase-js';

// Dùng cùng endpoint/key như backend để dữ liệu đồng bộ
const SUPABASE_URL = 'https://odmtndvllclmrwczcyvs.supabase.co';

// Publishable key (được phép dùng phía client khi RLS đã tắt hoặc đã cấu hình)
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kbXRuZHZsbGNsbXJ3Y3pjeXZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNDI0NDIsImV4cCI6MjA3OTYxODQ0Mn0.au4mfOQSocrCr9eC753wiveR1KI0TNAVxOk1KB5poMA';

export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

// Nếu bạn muốn import default:
// export default supabase;

