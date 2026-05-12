// Frida hook for the SC family Cloud PC RSA vmId encryption path.
//
// Usage:
//   frida -p <official-client-pid> -l hook_sc_rsa_frida.js
//
// Keep this running, then trigger one official family-cloud connection.
// The hook prints the plaintext passed to SecKeyCreateEncryptedData and the
// resulting 128-byte RSA ciphertext encoded as SDK-style base64url without "=".

const CFDataGetLength = new NativeFunction(
  Module.getExportByName(null, "CFDataGetLength"),
  "long",
  ["pointer"]
);
const CFDataGetBytePtr = new NativeFunction(
  Module.getExportByName(null, "CFDataGetBytePtr"),
  "pointer",
  ["pointer"]
);

const b64chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

function base64Encode(bytes) {
  let out = "";
  for (let i = 0; i < bytes.length; i += 3) {
    const a = bytes[i];
    const b = i + 1 < bytes.length ? bytes[i + 1] : 0;
    const c = i + 2 < bytes.length ? bytes[i + 2] : 0;
    const n = (a << 16) | (b << 8) | c;
    out += b64chars[(n >> 18) & 63];
    out += b64chars[(n >> 12) & 63];
    out += i + 1 < bytes.length ? b64chars[(n >> 6) & 63] : "=";
    out += i + 2 < bytes.length ? b64chars[n & 63] : "=";
  }
  return out;
}

function base64UrlNoPad(bytes) {
  return base64Encode(bytes).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function readCFDataBytes(cfdata) {
  if (cfdata.isNull()) return null;
  const len = Number(CFDataGetLength(cfdata));
  if (len <= 0 || len > 4096) return null;
  const ptr = CFDataGetBytePtr(cfdata);
  if (ptr.isNull()) return null;
  const buf = Memory.readByteArray(ptr, len);
  return Array.from(new Uint8Array(buf));
}

function asciiPreview(bytes) {
  let s = "";
  for (const b of bytes) {
    if (b >= 0x20 && b <= 0x7e) s += String.fromCharCode(b);
    else s += ".";
  }
  return s;
}

const secKeyCreateEncryptedData = Module.getExportByName(
  "Security",
  "SecKeyCreateEncryptedData"
);

Interceptor.attach(secKeyCreateEncryptedData, {
  onEnter(args) {
    this.plain = readCFDataBytes(args[2]);
  },
  onLeave(retval) {
    const encrypted = readCFDataBytes(retval);
    if (!this.plain || !encrypted || encrypted.length !== 128) return;
    const plainText = asciiPreview(this.plain);
    console.log(
      "[HOOK] SecKeyCreateEncryptedData"
      + " plain_len=" + this.plain.length
      + " plain_ascii=" + JSON.stringify(plainText)
      + " cipher_len=" + encrypted.length
      + " cipher_b64url=" + base64UrlNoPad(encrypted)
    );
  },
});

console.log("[HOOK] SecKeyCreateEncryptedData hook installed");
