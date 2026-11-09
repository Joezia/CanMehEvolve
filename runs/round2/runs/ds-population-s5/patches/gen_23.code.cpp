FIT_UINT8 Field::GetNum(void) const
{
    const Profile::PROFILE *p = profile;
    if (__builtin_expect(p == NULL, 0))
        return FIT_FIELD_NUM_INVALID;

    const Profile::FIELD *fields = p->fields;
    if (__builtin_expect((fields == NULL) | (profileIndex >= p->numFields), 0))
        return FIT_FIELD_NUM_INVALID;

    return fields[profileIndex].num;
}
