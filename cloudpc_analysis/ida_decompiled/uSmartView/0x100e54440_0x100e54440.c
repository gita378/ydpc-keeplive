// 0x100e54440 @ 0x100e54440
__int64 __fastcall spice_display_init(const char *a1, __int64 a2, __int64 a3, __int64 a4, __int64 a5, __int64 a6)
{
  __int64 v6; // rdx
  __int64 v7; // rcx
  __int64 v8; // r8
  __int64 v9; // r9
  __int64 v11; // [rsp+0h] [rbp-30h]
  unsigned int v12; // [rsp+Ch] [rbp-24h]
  int v13; // [rsp+10h] [rbp-20h]
  int v14; // [rsp+14h] [rbp-1Ch]
  int v15; // [rsp+18h] [rbp-18h]
  int v16; // [rsp+1Ch] [rbp-14h]
  __int64 v17; // [rsp+20h] [rbp-10h]
  int v18; // [rsp+28h] [rbp-8h]

  v18 = (int)a1; /*0x100e54448*/
  v17 = a2; /*0x100e5444b*/
  v16 = a3; /*0x100e5444f*/
  v15 = a4; /*0x100e54452*/
  v14 = a5; /*0x100e54455*/
  v13 = a6; /*0x100e54459*/
  if ( (unsigned int)spice_util_get_debug(a1, a2, a3, a4, a5, a6) && spice_gtk_log_level < 2 ) /*0x100e54475*/
  {
    a1 = "GSpice"; /*0x100e5447b*/
    a2 = 64; /*0x100e54482*/
    g_log( /*0x100e5449d*/
      (unsigned int)"GSpice",
      64,
      (unsigned int)"[%-38s:%4d] spice_display_init begin to init display ",
      (unsigned int)"spice_display_init",
      643,
      v9);
  }
  v12 = 0; /*0x100e544a9*/
  if ( v18 ) /*0x100e544b3*/
  {
    if ( (unsigned int)spice_util_get_debug(a1, a2, v6, v7, v8, v9) && spice_gtk_log_level < 2 ) /*0x100e544d6*/
      g_log( /*0x100e54502*/
        (unsigned int)"GSpice",
        64,
        (unsigned int)"[%-38s:%4d] channel_id is %d, will not change video init.",
        (unsigned int)"spice_display_init",
        646,
        v18);
    return 0; /*0x100e5450f*/
  }
  else
  {
    v11 = *(_QWORD *)(v17 + 24); /*0x100e54523*/
    if ( !*(_QWORD *)(v11 + 96) ) /*0x100e5452b*/
      *(_QWORD *)(v11 + 96) = g_malloc_n(1, 16); /*0x100e54548*/
    if ( *(_QWORD *)(v11 + 96) ) /*0x100e54550*/
    {
      **(_DWORD **)(v11 + 96) = v16; /*0x100e54566*/
      *(_DWORD *)(*(_QWORD *)(v11 + 96) + 8LL) = v14; /*0x100e54573*/
      *(_DWORD *)(*(_QWORD *)(v11 + 96) + 4LL) = v15; /*0x100e54581*/
      *(_DWORD *)(*(_QWORD *)(v11 + 96) + 12LL) = v13; /*0x100e5458f*/
      return 1; /*0x100e54592*/
    }
    return v12; /*0x100e5459c*/
  }
}
