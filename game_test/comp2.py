def update_array(self):
    self.screen_width = self.size.width
    self.screen_height = self.size.height

    self.render_array = [[Segment(' ', Style.parse("grey89") + Style(bgcolor="cyan")) for _ in range(self.screen_width)] for _ in range(self.screen_height)]

    if self.local_player_id > 0 and self.fully_received > 0:
        start_time = time.time()
        world = self.local_server.game_world
        half_width = self.screen_width // 2
        half_height = self.screen_height // 2

        my_character = world[self.local_player_id]
        char_pos = my_character.components[Position]
        char_rend = my_character.components[Renderable]
        char_chunk_x = my_character.components[MapChunkPosition].x
        char_chunk_y = my_character.components[MapChunkPosition].y
        char_chunk_z = my_character.components[MapChunkPosition].z

        offset_x = char_pos.x - half_width
        offset_y = char_pos.y - half_height

        terrain_union = set()
        overworld_union = set()

        log_message = self.Updated(my_character)
        random_message = self.Randomdata(half_width, half_height)

        self.post_message(log_message)
        self.post_message(random_message)

        for x_off in [-2, -1, 0, 1, 2]:
            for y_off in [-2, -1, 0, 1, 2]:
                for z_off in [-1, 0, 1]:
                    terrain_union |= world.Q.all_of(components=[Terrain], tags=[MapChunkPosition(char_chunk_x + x_off, char_chunk_y + y_off, char_chunk_z + z_off)])
                    overworld_union |= world.Q.all_of(components=[In_Overworld], tags=[MapChunkPosition(char_chunk_x + x_off, char_chunk_y + y_off, char_chunk_z + z_off)])

        priority_list = [[0] * self.screen_width for _ in range(self.screen_height)]

        def tint_color(my_z_diff, my_color):
            if my_z_diff > 0:
                tint_factor = my_z_diff / 40
                aR, aG, aB = 255, 255, 255
            else:
                shade_factor = -my_z_diff / 10
                aR, aG, aB = 0, 0, 0
            newR = my_color[0] + (aR - my_color[0]) * tint_factor
            newG = my_color[1] + (aG - my_color[1]) * tint_factor
            newB = my_color[2] + (aB - my_color[2]) * tint_factor
            newR = int(max(0, min(newR, 255))
            newG = int(max(0, min(newG, 255))
            newB = int(max(0, min(newB, 255))
            return f"rgb({newR},{newG},{newB})"

        def draw_ents(ent_set_union, my_char_pos):
            for ent in ent_set_union:
                pos = ent.components[Position]
                rend = ent.components[Renderable]
                if (abs(pos.x - my_char_pos.x) < half_width) and (abs(pos.y - my_char_pos.y) < half_height):
                    z_diff = my_char_pos.z - pos.z
                    rgb = rend.color
                    bgrgb = rend.bgcolor
                    front_color = tint_color(z_diff, rgb)
                    back_color = tint_color(z_diff, bgrgb)
                    ent_char = rend.char
                    render_x = pos.x - offset_x
                    render_y = pos.y - offset_y
                    true_prio = (pos.z * 10) + rend.priority
                    if priority_list[render_y][render_x] < true_prio:
                        priority_list[render_y][render_x] = true_prio
                        final_style = ""
                        if bgrgb == TRANSPARENT_COLOR:
                            bgtouse = self.render_array[render_y][render_x].style.bgcolor
                            final_style = Style.parse(front_color) + Style(bgcolor=bgtouse)
                        else:
                            final_style = Style.parse(front_color) + Style(bgcolor=back_color)
                        self.render_array[render_y][render_x] = Segment(ent_char, final_style)

        draw_ents(terrain_union, char_pos)
        draw_ents(overworld_union, char_pos)
        end_time = time.time()
        elapse = end_time - start_time
        self.client_sio.emit("print", "RENDER ELAPSED TIME IS")
        self.client_sio.emit("print", elapse)
