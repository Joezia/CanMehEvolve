FIT_UINT8 Field::GetNum(void) const
{
    const auto *p = profile;
    if (__builtin_expect(p == NULL, 0))
        return FIT_FIELD_NUM_INVALID;

    const Profile::FIELD *fields = p->fields;
    const FIT_UINT8 index = profileIndex;
    if (__builtin_expect((fields == NULL) | (index >= p->numFields), 0))
        return FIT_FIELD_NUM_INVALID;

    return fields[index].num;
}
