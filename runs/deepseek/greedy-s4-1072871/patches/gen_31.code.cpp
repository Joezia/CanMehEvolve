Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    Field* field = fields.data();
    auto count = fields.size();

    while (count >= 4)
    {
        if (*reinterpret_cast<const FIT_UINT8*>(field) == fieldNum)
            return field;
        if (*reinterpret_cast<const FIT_UINT8*>(field + 1) == fieldNum)
            return field + 1;
        if (*reinterpret_cast<const FIT_UINT8*>(field + 2) == fieldNum)
            return field + 2;
        if (*reinterpret_cast<const FIT_UINT8*>(field + 3) == fieldNum)
            return field + 3;

        field += 4;
        count -= 4;
    }

    while (count > 0)
    {
        if (*reinterpret_cast<const FIT_UINT8*>(field) == fieldNum)
            return field;
        ++field;
        --count;
    }

    return FIT_NULL;
}
