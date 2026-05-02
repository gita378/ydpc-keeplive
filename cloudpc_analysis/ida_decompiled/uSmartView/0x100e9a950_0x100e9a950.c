// 0x100e9a950 @ 0x100e9a950
__int64 __fastcall sub_100E9A950(__int64 a1, __int64 a2, __int64 a3, __int64 a4, __int64 a5, __int64 a6)
{
  __int64 result; // rax
  __int64 v7; // rcx
  int v8; // [rsp+0h] [rbp-50h]
  __int64 v9; // [rsp+30h] [rbp-20h]

  result = (unsigned __int8)byte_103346148; /*0x100e9a963*/
  if ( byte_103346148 ) /*0x100e9a96d*/
  {
    result = *(_QWORD *)(a1 + 200); /*0x100e9a977*/
    if ( *(_QWORD *)(result + 176) ) /*0x100e9a97e*/
    {
      result = *(_QWORD *)(*(_QWORD *)(a1 + 200) + 176LL); /*0x100e9a997*/
      v7 = *(unsigned __int8 *)(result + 25232); /*0x100e9a99e*/
      if ( *(_BYTE *)(result + 25232) ) /*0x100e9a99e*/
      {
        result = *(_QWORD *)(*(_QWORD *)(a1 + 200) + 176LL); /*0x100e9a9b9*/
        if ( !*(_BYTE *)(result + 27245) ) /*0x100e9a9c0*/
        {
          v9 = *(_QWORD *)(*(_QWORD *)(*(_QWORD *)(a1 + 200) + 176LL) + 304LL); /*0x100e9a9e6*/
          if ( (unsigned int)spice_util_get_debug(a1, a2, a3, v7, a5, a6) ) /*0x100e9a9ea*/
          {
            if ( spice_gtk_log_level < 2 ) /*0x100e9aa02*/
            {
              v8 = *(_DWORD *)(*(_QWORD *)(*(_QWORD *)(a1 + 200) + 176LL) + 16LL); /*0x100e9aa4b*/
              g_log( /*0x100e9aa51*/
                (unsigned int)"GSpice",
                64,
                (unsigned int)"[%-38s:%4d] create stream %d conv:%x",
                (unsigned int)"create_stream_on_link_message",
                4530,
                a2,
                v8);
            }
          }
          result = ikcp_do_stream_create( /*0x100e9aad4*/
                     *(_QWORD *)(*(_QWORD *)(a1 + 200) + 176LL),
                     (unsigned __int8)a2,
                     *(unsigned __int8 *)(a3 + 2),
                     a1,
                     (unsigned int)tn_stream_read_notify_cb,
                     (unsigned int)tn_stream_write_notify_cb,
                     *(unsigned __int8 *)(*(_QWORD *)(*(_QWORD *)(a1 + 200) + 176LL) + 18469LL),
                     *(_QWORD *)(v9 + 112));
          *(_QWORD *)(a1 + 184) = result; /*0x100e9aadd*/
        }
      }
    }
  }
  return result; /*0x100e9aae4*/
}
