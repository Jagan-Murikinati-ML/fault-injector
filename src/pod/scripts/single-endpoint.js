import http from 'k6/http';
import { check, fail } from 'k6';

export let options = {
    vus: __ENV.CHAOS_K6_VUS ? parseInt(__ENV.CHAOS_K6_VUS) : 1,
    duration: __ENV.CHAOS_K6_DURATION || '10s',
};

export default function () {
    const url = __ENV.CHAOS_K6_URL;
    if (!url) {
        fail("❌ No CHAOS_K6_URL provided");
    }

    const token = __ENV.CHAOS_K6_LOGIN_TOKEN;
    let params = { headers: {} };

    if (token) {
        params.headers['Cookie'] = `login_token=${token}`;
    }

    // Optional: add additional headers
    if (__ENV.CHAOS_K6_HEADERS) {
        try {
            const extraHeaders = JSON.parse(__ENV.CHAOS_K6_HEADERS);
            Object.assign(params.headers, extraHeaders);
        } catch (err) {
            fail("❌ Invalid CHAOS_K6_HEADERS JSON: " + err.message);
        }
    }

    const res = http.get(url, params);

    const success = check(res, {
        "status is 200": (r) => r.status === 200,
    });

    if (!success) {
        console.error(`⚠️ Request failed:
  URL: ${url}
  Status: ${res.status}
  Body: ${res.body.substring(0, 200)}...`);
    } else {
        console.log(`✅ Success:
  URL: ${url}
  Status: ${res.status}`);
    }
}
