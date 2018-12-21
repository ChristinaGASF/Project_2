// helper function
// get values from cookie with key
function getFromCookie(key) {
    
    if (!document.cookie) return null;
  
    const xsrfCookies = document.cookie.split(';').map(c => c.trim()).filter(c => c.startsWith(`${key}=`));
  
    if (xsrfCookies.length === 0) return null;

    return decodeURIComponent(xsrfCookies[0].split('=')[1]);
}
