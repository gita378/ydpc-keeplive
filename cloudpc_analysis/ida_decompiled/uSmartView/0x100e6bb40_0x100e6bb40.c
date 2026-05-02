// 0x100e6bb40 @ 0x100e6bb40
__int64 __fastcall ice_deal_kcp_common_data(
        __int64 a1,
        unsigned int a2,
        unsigned int a3,
        __int64 a4,
        unsigned __int16 a5)
{
  int v5; // r8d
  int v6; // r9d
  __int64 ms; // rax
  __int64 v8; // rdx
  __int64 v9; // r8
  __int64 v10; // r9
  __int64 v11; // rcx
  unsigned int v12; // eax
  __int64 kcp_by_conv; // [rsp+30h] [rbp-40h]
  __int64 v15; // [rsp+38h] [rbp-38h]
  __int64 v16; // [rsp+40h] [rbp-30h]
  int v17; // [rsp+5Ch] [rbp-14h]

  kcp_by_conv = ice_get_kcp_by_conv(*(_QWORD *)(a1 + 136), a4, a5, a3); /*0x100e6bb7b*/
  if ( kcp_by_conv ) /*0x100e6bb97*/
  {
    v17 = ikcp_check_udp_data((_BYTE *)kcp_by_conv, a1 + 172, a2); /*0x100e6bbcd*/
    if ( v17 > 0 ) /*0x100e6bbe1*/
    {
      v15 = *(_QWORD *)(kcp_by_conv + 304); /*0x100e6bc02*/
      if ( *(_QWORD *)(v15 + 104) ) /*0x100e6bc0a*/
      {
        ms = ice_get_ms(); /*0x100e6bc3c*/
        v11 = v15; /*0x100e6bc41*/
        *(_QWORD *)(v15 + 72) = ms; /*0x100e6bc45*/
        if ( (unsigned __int64)(*(_QWORD *)(v15 + 72) - qword_10333A260) >= 0x7D0 ) /*0x100e6bc5e*/
        {
          qword_10333A260 = *(_QWORD *)(v15 + 72); /*0x100e6bc6c*/
          if ( (unsigned int)spice_util_get_debug(kcp_by_conv, a1 + 172, v8, v15, v9, v10) ) /*0x100e6bc73*/
          {
            if ( spice_gtk_log_level < 1 ) /*0x100e6bc8b*/
              g_log( /*0x100e6bcf3*/
                (unsigned int)"GSpice",
                128,
                (unsigned int)"[%-38s:%4d] conv:%u snd_nxt:%u, rcv_nxt:%u touch:%llu",
                (unsigned int)"ice_deal_kcp_common_data",
                1549,
                *(_DWORD *)(kcp_by_conv + 16),
                *(_DWORD *)(kcp_by_conv + 40),
                *(_DWORD *)(kcp_by_conv + 44),
                *(_QWORD *)(v15 + 72));
          }
        }
        ikcp_input((_DWORD *)kcp_by_conv, (unsigned __int8 *)(a1 + 172), v17, v11, v9, v10); /*0x100e6bd17*/
        if ( *(_BYTE *)(v15 + 49) == (*(_QWORD *)(v15 + 40) != 0) /*0x100e6bd5f*/
          || ((*(void (__fastcall **)(__int64))(v15 + 120))(v15), *(_BYTE *)(v15 + 49)) )
        {
          *(_WORD *)(v15 + 168) = 1; /*0x100e6bd90*/
          v16 = *(_QWORD *)(v15 + 104); /*0x100e6bda1*/
          if ( *(_WORD *)(v16 + 170) || (*(_DWORD *)(v16 + 28) & 1) != 0 ) /*0x100e6bdc6*/
          {
            v12 = ice_iclock(*(_QWORD *)(kcp_by_conv + 12428)); /*0x100e6bde2*/
            ikcp_update(kcp_by_conv, v12); /*0x100e6bded*/
            return 0; /*0x100e6bdf2*/
          }
          else
          {
            if ( (*(_DWORD *)(v16 + 28) & 4) == 0 && (int)ikcp_waitsnd(kcp_by_conv) < 75 ) /*0x100e6be1c*/
              ice_set_socket_flag_ex(v16, 4, 1573); /*0x100e6be30*/
            *(_WORD *)(v16 + 166) = 1; /*0x100e6be39*/
            (*(void (__fastcall **)(__int64))(v16 + 128))(v16); /*0x100e6be51*/
            return 0; /*0x100e6be53*/
          }
        }
        else
        {
          return 0; /*0x100e6bd77*/
        }
      }
      else
      {
        LOBYTE(v5) = v17 <= 0; /*0x100e6bbd7*/
        ikcp_input((_DWORD *)kcp_by_conv, (unsigned __int8 *)(a1 + 172), v17, 0, v5, v6); /*0x100e6bc2a*/
        return 2; /*0x100e6bc2f*/
      }
    }
    else
    {
      return 2; /*0x100e6bbe7*/
    }
  }
  else
  {
    return 1; /*0x100e6bb9d*/
  }
}
