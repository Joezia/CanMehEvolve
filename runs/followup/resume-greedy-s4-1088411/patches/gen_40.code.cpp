Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    Field* field = fields.data();
    const std::size_t count = fields.size();

    for (std::size_t i = 0; i < count; ++i)
    {
        if (static_cast<FIT_UINT8>(field[i].num) == fieldNum)
            return &field[i];
    }

    return FIT_NULL;
}
