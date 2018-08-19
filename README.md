# CharacterBot
A Discord bot that can turn users into their favourite characters!

## Installation
First and foremost, you need to add it to your Discord server by using
[this link](https://bit.ly/CharacterBotInvite).

## Setup
The bot is still in its early stages and it doesn't have a Web version for now, but we've tried to make the setup as easy as we can!
It's recommended that you set up the bot in a dedicated `#bot-commands` channel, possibly a private one,
so that you don't spam your members with useless notifications.

We also have some pre-made templates for some fanbases,
so if you're feeling lucky jump right to the **Importing Premade Databases** section.

### Generating the template
Now that you have just installed the bot, you need to add all your characters.
This is what your database will look like:

```
| name    |
|---------|
```

By default, a character only has an id called `name` attached to it, but that's pretty boring, right?
Let's add some more columns.

To do that, you'll need to use the `>>char template` command.
Let's say we wanted to add a `sex` and an `age` field, here's how we would do it:

```
>>char template sex age
```

Now our database will look like this:

```
| name | sex | age |
|------|-----|-----|
```

A few things to note:
- If you need to put spaces in one of the fields' name, use underscores (`example_field`) or camel case (`exampleField`)
- There are a few field names that do something special if you add them
    - `discord_role` should contain the discord role assigned to the character. Case sensitive: `class1a` is different from `Class1A`
    - `thumbnail` will display a small image when checking the character's info. It should contain an url leading to the image.
    - `image` will display a big image when checking the character's info. Like `thumbnail`, this should be an url

### Creating different tables
Let's say you want to sort your characters.
Whether you need to group them based on which seasons or guilds they are in, you can do that with the `>>char create` command.

Let's say we're making a Boku no Hero Academia database. We'd need to separate characters from Class 1A and Class 1B.
To do that, let's do:

```
>>char create Class1A
>>char create Class1B
```

Now we have two empty tables called Class1A and Class1B:

```
Class1A
| name | sex | age |
|------|-----|-----|

Class1B
| name | sex | age |
|------|-----|-----|
```

Please note that, like the template, you **can't** put spaces in table names. Use underscores if you need to.

### Adding characters to the tables
Now it's time to actually add the characters. To do that, we'll use the `>>char add` command.
For example, let's add Deku to Class1A:

```
>>char add Class1A Deku M 16
```

We first passed the table we wanted to put Deku in (`Class1A`),
then the name of the character (`Deku`)
and lastly the two arguments we put way back in `>>char template`.

Let's populate our tables some more and check the results.

```
>>char add Class1A Bakugo M 16
>>char add Class1A Uraraka F 16

>>char add Class1B Itsuka F 16
>>char add Class1B Neito M 16
```

```
Class1A
| name    | sex | age |
|---------|-----|-----|
| Deku    | M   | 16  |
| Bakugo  | M   | 16  |
| Uraraka | F   | 16  |

Class1B
| name   | sex | age |
|--------|-----|-----|
| Itsuka | F   | 16  |
| Neito  | M   | 16  |
```

A few things to note:
- The `Name` parameter doesn't actually need to be the name of the character. It should be something easily recognizable (like Deku instead of Izuku)
- If you need to put spaces, you need to put the whole thing in quotation marks. EG: `>>char add Class1A Deku "He is Male" 16`. This applies to the `name` as well
- You need to put the extra fields (in this case `sex` and `age`) in the exact same order you put them in `>>char template`
- You can't have a character named like a table
- You can't have two characters with the same name, **even if different tables**

### Deleting characters and tables
Messed up? Don't worry, you can undo it.
The `>>char del` and `>>char add` commands can delete and modify tables and characters. Let's say we typed:

```
>>char add Class1B Neito 16 M
>>char add Class1B Tsuyu F 16
>>char create Còass1C
```

```
Class1A
| name    | sex | age |
|---------|-----|-----|
| Deku    | M   | 16  |
| Bakugo  | M   | 16  |
| Uraraka | F   | 16  |

Class1B
| name   | sex | age |
|--------|-----|-----|
| Itsuka | F   | 16  |
| Neito  | 16  | M   |
| Tsuyu  | F   | 16  |

Còass1C
| name   | sex | age |
|--------|-----|-----|
```

What a mess! I swapped Neito's fields, put Tsuyu in the wrong table and mispelled Class1C! Let's fix all of this.

#### Modifying character info
Let's fix Neito's row. It's very simple to do: just run `>>char add` again, but this time with the right fields:

```
>>char add Class1B Neito M 16
```

`>>char add` will modify a character's info if it already exists. Now Naito's data is correct!
```
Class1B
| name   | sex | age |
|--------|-----|-----|
| Itsuka | F   | 16  |
| Neito  | M   | 16  |
| Tsuyu  | F   | 16  |
```

#### Deleting a character or a table
Let's put Tsuyu in Class1A. But first, we need to delete her from Class1B. To do that, just run:

```
>>char del Tsuyu
>>char add Class1A Tsuyu F 16
```

And now let's get rid of the Còass1C table. To delete tables, run `>>char del` like you would do with a character.

```
>>char del Còass1C
```

Now all of our data is correct!
```
Class1A
| name    | sex | age |
|---------|-----|-----|
| Deku    | M   | 16  |
| Bakugo  | M   | 16  |
| Uraraka | F   | 16  |
| Tsuyu   | F   | 16  |

Class1B
| name   | sex | age |
|--------|-----|-----|
| Itsuka | F   | 16  |
| Neito  | 16  | M   |
| Tsuyu  | F   | 16  |
```

Be careful when deleting a table, as it will delete all of its contents as well!

## Importing Pre-made Databases
To import a pre-made database, use the command `>>import`.
Let's say we want to import a Boku no Hero Academia database. We'd do:

```
>>import bnha
```

It's that easy.

If you want to check which presets we have available, run `>>import list`.


