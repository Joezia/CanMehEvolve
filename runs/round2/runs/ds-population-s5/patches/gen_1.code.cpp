FIT_UINT8 Field::GetNum(void) const
{
    const Profile::FIELD *fields = (profile != NULL) ? profile->fields : NULL;
    if (__builtin_expect((fields == NULL) || (profileIndex >= profile->numFields), 0))
        return FIT_FIELD_NUM_INVALID;
    return fields[profileIndex].num;
}
