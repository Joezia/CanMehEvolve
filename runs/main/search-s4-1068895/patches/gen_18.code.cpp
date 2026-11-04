
void SetActiveTime(FIT_UINT32 activeTime)
{
    // Direct field write avoids function call overhead and subfield lookup
    fields[6].value.u32 = activeTime;
    fields[6].is_valid = true;
}
