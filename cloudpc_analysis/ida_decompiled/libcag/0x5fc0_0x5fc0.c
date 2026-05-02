// 0x5fc0 @ 0x5fc0
__int64 __fastcall generate_http_msg(__int64 a1, int a2, __int64 a3, int a4)
{
  if ( a3 )
  {
    if ( (unsigned int)check_ip_addr_family_cag(a1) == 2 )
      return ZXSnprintf(
               a4,
               256,
               (unsigned int)"CONNECT [%s]:%d HTTP/1.1\r\n"
                             "Host: %s:%d\r\n"
                             "Proxy-Connection: keep-alive\r\n"
                             "Proxy-Authorization: Basic %s\r\n"
                             "\r\n",
               a1,
               a2,
               a1,
               a2,
               a3);
    else
      return ZXSnprintf(
               a4,
               256,
               (unsigned int)"CONNECT %s:%d HTTP/1.1\r\n"
                             "Host: %s:%d\r\n"
                             "Proxy-Connection: keep-alive\r\n"
                             "Proxy-Authorization: Basic %s\r\n"
                             "\r\n",
               a1,
               a2,
               a1,
               a2,
               a3,
               a3);
  }
  else if ( (unsigned int)check_ip_addr_family_cag(a1) == 2 )
  {
    return ZXSnprintf(
             a4,
             256,
             (unsigned int)"CONNECT [%s]:%d HTTP/1.1\r\nHost: %s:%d\r\nProxy-Connection: keep-alive\r\n\r\n",
             a1,
             a2,
             a1,
             a2);
  }
  else
  {
    return ZXSnprintf(
             a4,
             256,
             (unsigned int)"CONNECT %s:%d HTTP/1.1\r\nHost: %s:%d\r\nProxy-Connection: keep-alive\r\n\r\n",
             a1,
             a2,
             a1,
             a2);
  }
}
