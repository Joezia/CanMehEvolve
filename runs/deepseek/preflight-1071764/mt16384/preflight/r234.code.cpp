Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    Field* data = fields.data();
    auto count = fields.size();
    for (decltype(count) i = 0; i < count; ++i)
    {
        if (*reinterpret_cast<const unsigned char*>(&data[i]) == fieldNum)
            return &data[i];
    }

    return FIT_NULL;
}
