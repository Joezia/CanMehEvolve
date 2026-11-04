Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    Field* field = fields.data();
    auto count = fields.size();

    while (count >= 4)
    {
        if (field[0].GetNum() == fieldNum) return &field[0];
        if (field[1].GetNum() == fieldNum) return &field[1];
        if (field[2].GetNum() == fieldNum) return &field[2];
        if (field[3].GetNum() == fieldNum) return &field[3];
        field += 4;
        count -= 4;
    }

    while (count != 0)
    {
        if (field->GetNum() == fieldNum)
            return field;
        ++field;
        --count;
    }

    return FIT_NULL;
}
