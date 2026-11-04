FIT_UINT8 Field::GetNum(void) const
{
    const FIT_PROFILE_MESG *p = profile;
    if (__builtin_expect((p != NULL) && (profileIndex < p->numFields), 1))
        return p->fields[profileIndex].num;
    return FIT_FIELD_NUM_INVALID;
}
