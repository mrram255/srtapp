/** In-memory copy of the access JWT for Authorization headers on Django requests (cookie stays httpOnly). */
let memoryAccessToken: string | null = null;

export function setMemoryAccessToken(token: string | null) {
  memoryAccessToken = token;
}

export function getMemoryAccessToken(): string | null {
  return memoryAccessToken;
}

export function clearMemoryAccessToken() {
  memoryAccessToken = null;
}
