// 0x100e8ade0 @ 0x100e8ade0
void __fastcall sub_100E8ADE0(unsigned __int16 *a1, __int64 a2, __int64 a3, __int64 a4, __int64 a5, __int64 a6)
{
  const char *v6; // r10
  int v7; // [rsp+40h] [rbp-90h]

  if ( a1 && (unsigned int)spice_util_get_debug(a1, a2, a3, a4, a5, a6) && spice_gtk_log_level < 2 )
  {
    v6 = "N"; /*0x100e8ae6d*/
    if ( *((_BYTE *)a1 + 78) ) /*0x100e8ae5d*/
      v6 = "Y"; /*0x100e8ae74*/
    v7 = *((_DWORD *)a1 + 21); /*0x100e8af33*/
    g_log(
      (unsigned int)"GSpice",
      64,
      (unsigned int)"[%-38s:%4d] Channel Link Socket Info: Type=%u, Port=%u, Priority=%u, LinkType=%u, Protocol=%u, Emerg"
                    "ency=%s, BW=%uKB/s, TotalBW=%uKB/s, QoS=0x%02X, ChannelType=%u(0x%02X), Extend=[0x%08X,0x%08X,0x%08X,0x%08X]",
      (unsigned int)"print_channel_link_info_ex",
      4808,
      a1[77],
      *a1,
      *((unsigned __int8 *)a1 + 2),
      *((unsigned __int8 *)a1 + 3),
      *((unsigned __int8 *)a1 + 77),
      v6,
      *(unsigned __int16 *)((char *)a1 + 79),
      *(unsigned __int16 *)((char *)a1 + 81),
      *((unsigned __int8 *)a1 + 83),
      v7,
      (unsigned __int8)v7,
      *((_DWORD *)a1 + 22),
      *((_DWORD *)a1 + 23),
      *((_DWORD *)a1 + 24),
      *((_DWORD *)a1 + 25));
  }
}
