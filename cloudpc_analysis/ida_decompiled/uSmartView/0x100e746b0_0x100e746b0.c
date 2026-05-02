// 0x100e746b0 @ 0x100e746b0
__int64 __fastcall ikcp_send(__int64 a1, __int64 a2, __int64 a3, __int64 a4, __int64 a5, __int64 a6)
{
  __int64 v6; // rdx
  __int64 v7; // rcx
  __int64 v8; // r8
  __int64 v9; // r9
  int v11; // [rsp+0h] [rbp-60h]
  int v12; // [rsp+10h] [rbp-50h]
  __int64 v13; // [rsp+20h] [rbp-40h]
  int v14; // [rsp+2Ch] [rbp-34h]
  int i; // [rsp+30h] [rbp-30h]
  int v16; // [rsp+34h] [rbp-2Ch]
  __int64 v17; // [rsp+38h] [rbp-28h]
  unsigned int v18; // [rsp+44h] [rbp-1Ch]
  __int64 v19; // [rsp+48h] [rbp-18h]

  v19 = a2; /*0x100e746bc*/
  v18 = a3; /*0x100e746c0*/
  v14 = a3; /*0x100e746c6*/
  if ( !*(_WORD *)(a1 + 26) && (unsigned int)spice_util_get_debug(a1, a2, a3, *(unsigned __int16 *)(a1 + 26), a5, a6) ) /*0x100e746e4*/
    g_log( /*0x100e7471b*/
      (unsigned int)"GSpice",
      8,
      (unsigned int)"[%-38s:%4d] assertion `%s' failed",
      (unsigned int)"ikcp_send",
      1010,
      (unsigned int)"kcp->mss > 0");
  if ( v14 >= 0 )
  {
    *(_DWORD *)(a1 + 12420) = *(_DWORD *)(a1 + 96); /*0x100e74767*/
    if ( !*(_DWORD *)(a1 + 12328)
      || a1 + 184 == *(_QWORD *)(a1 + 184)
      || (v13 = *(_QWORD *)(a1 + 192), *(unsigned __int16 *)(v13 + 36) >= (int)*(unsigned __int16 *)(a1 + 26))
      || (v14 >= *(unsigned __int16 *)(a1 + 26) - *(unsigned __int16 *)(v13 + 36)
        ? (v12 = *(unsigned __int16 *)(a1 + 26) - *(unsigned __int16 *)(v13 + 36))
        : (v12 = v14),
          ZXMemcpy(*(unsigned __int16 *)(v13 + 36) + *(_QWORD *)(v13 + 88), v12, a2, v12),
          v19 = v12 + a2,
          *(_WORD *)(v13 + 36) += v12,
          v14 -= v12,
          v14 > 0) )
    {
      if ( v14 > *(unsigned __int16 *)(a1 + 26) ) /*0x100e7489e*/
        v16 = (*(unsigned __int16 *)(a1 + 26) + v14 - 1) / *(unsigned __int16 *)(a1 + 26); /*0x100e748d1*/
      else
        v16 = 1; /*0x100e748a4*/
      for ( i = 0; i < v16; ++i ) /*0x100e748d4*/
      {
        if ( v14 <= *(unsigned __int16 *)(a1 + 26) ) /*0x100e748f4*/
          v11 = v14; /*0x100e7490d*/
        else
          v11 = *(unsigned __int16 *)(a1 + 26); /*0x100e74902*/
        v17 = ikcp_segment_new(a1, (unsigned int)v11); /*0x100e74922*/
        if ( !v17 && (unsigned int)spice_util_get_debug(a1, (unsigned int)v11, v6, v7, v8, v9) ) /*0x100e7493b*/
          g_log( /*0x100e74972*/
            (unsigned int)"GSpice",
            8,
            (unsigned int)"[%-38s:%4d] assertion `%s' failed",
            (unsigned int)"ikcp_send",
            1044,
            (unsigned int)"seg");
        if ( !v17 ) /*0x100e7499d*/
          return (unsigned int)-2; /*0x100e749aa*/
        ZXMemcpy(*(_QWORD *)(v17 + 88), v11, v19, v11); /*0x100e749c8*/
        ++*(_DWORD *)(a1 + 148); /*0x100e749dc*/
        *(_WORD *)(v17 + 36) = v11; /*0x100e749eb*/
        *(_QWORD *)v17 = v17; /*0x100e749f8*/
        *(_QWORD *)(v17 + 8) = v17; /*0x100e74a03*/
        *(_QWORD *)(v17 + 8) = *(_QWORD *)(a1 + 192); /*0x100e74a16*/
        *(_QWORD *)v17 = a1 + 184; /*0x100e74a29*/
        **(_QWORD **)(a1 + 192) = v17; /*0x100e74a3b*/
        *(_QWORD *)(a1 + 192) = v17; /*0x100e74a46*/
        v19 += v11; /*0x100e74a5b*/
        v14 -= v11; /*0x100e74a6a*/
      }
      return v18; /*0x100e74a7f*/
    }
    else
    {
      return v18; /*0x100e7487a*/
    }
  }
  else
  {
    return (unsigned int)-1; /*0x100e7474b*/
  }
}
